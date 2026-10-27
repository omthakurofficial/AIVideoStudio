"""Minimal stdio MCP client (JSON-RPC 2.0, newline-delimited). Used for EffectCraft/FilmCraft headless servers.
Handles timeouts, process death, and structured errors. Logs tool names and durations, never secrets."""
from __future__ import annotations
import json, logging, queue, subprocess, threading, time
from typing import Any

log = logging.getLogger("aivs.mcp")


class EngineError(Exception):
    """Actionable failure from an external engine. `retryable` marks transient failures safe to retry."""
    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


class MCPClient:
    def __init__(self, cmd: list[str], name: str, timeout: float = 60.0, cwd: str | None = None):
        self.cmd, self.name, self.timeout, self.cwd = cmd, name, timeout, cwd
        self._p: subprocess.Popen | None = None
        self._q: queue.Queue[str | None] = queue.Queue()
        self._id = 0
        self._lock = threading.Lock()
        self.server_info: dict = {}
        self.tools: dict[str, dict] = {}

    def start(self) -> None:
        try:
            self._p = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                       text=True, bufsize=1, cwd=self.cwd)
        except FileNotFoundError:
            raise EngineError(f"{self.name} executable not found ({self.cmd[0]}). Install it or set its path in .env.")
        def pump():
            assert self._p and self._p.stdout
            for line in self._p.stdout:
                self._q.put(line)
            self._q.put(None)
        threading.Thread(target=pump, daemon=True).start()
        r = self._rpc("initialize", {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "aivs", "version": "0.1"}})
        self.server_info = r.get("serverInfo", {})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        cursor = None
        while True:
            tl = self._rpc("tools/list", {"cursor": cursor} if cursor else {})
            for t in tl["tools"]:
                self.tools[t["name"]] = t
            cursor = tl.get("nextCursor")
            if not cursor:
                break

    def _send(self, msg: dict) -> None:
        assert self._p and self._p.stdin
        try:
            self._p.stdin.write(json.dumps(msg) + "\n"); self._p.stdin.flush()
        except (BrokenPipeError, OSError):
            raise EngineError(f"{self.name} process exited unexpectedly.", retryable=True)

    def _rpc(self, method: str, params: dict) -> dict:
        with self._lock:
            self._id += 1; i = self._id
            self._send({"jsonrpc": "2.0", "id": i, "method": method, "params": params})
            end = time.time() + self.timeout
            while True:
                try:
                    line = self._q.get(timeout=max(0.1, end - time.time()))
                except queue.Empty:
                    self.close()
                    raise EngineError(f"{self.name} did not answer '{method}' within {self.timeout:.0f}s; the process was stopped.", retryable=True)
                if line is None:
                    raise EngineError(f"{self.name} process exited unexpectedly.", retryable=True)
                try:
                    m = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if m.get("id") == i:
                    if "error" in m:
                        raise EngineError(f"{self.name} {method}: {m['error'].get('message', m['error'])}")
                    return m.get("result", {})

    def call(self, tool: str, **args: Any) -> Any:
        """Call an MCP tool; returns parsed JSON when the text content is JSON, else the text. Raises EngineError on tool errors."""
        if tool not in self.tools:
            raise EngineError(f"{self.name} has no tool '{tool}' (version {self.server_info.get('version')}). Capability discovery shows: {sorted(self.tools)[:8]}…")
        t0 = time.time()
        res = self._rpc("tools/call", {"name": tool, "arguments": args})
        text = "\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
        log.debug("%s.%s %.2fs", self.name, tool, time.time() - t0)
        if res.get("isError"):
            raise EngineError(f"{self.name} {tool} failed: {text[:600]}")
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return text

    def close(self) -> None:
        p, self._p = self._p, None
        if p and p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()

    def __enter__(self): self.start(); return self
    def __exit__(self, *a): self.close()
