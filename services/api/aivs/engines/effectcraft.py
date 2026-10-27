"""EffectCraft adapter. Editing goes through the headless MCP server (`effectcraft-cli mcp`); video rendering goes through
`effectcraft-cli render` because the verified MCP tool set has no video export (only render_frame)."""
from __future__ import annotations
import logging, subprocess, time
from dataclasses import dataclass, field
from pathlib import Path
from .mcp_client import MCPClient, EngineError
from .media import verify_video, VideoFacts

log = logging.getLogger("aivs.effectcraft")

REQUIRED_TOOLS = {"batch", "execute_command", "save_project", "get_comp", "get_layer", "render_frame", "add_keyframe"}
REQUIRED_COMMANDS = {"comp.new", "layer.newShape", "layer.newText", "layer.newNull", "layer.setParent", "prop.addKey", "prop.set"}


@dataclass
class Capabilities:
    version: str
    tools: list[str]
    missing_tools: list[str] = field(default_factory=list)
    missing_commands: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing_tools and not self.missing_commands


class EffectCraftAdapter:
    def __init__(self, cli: str, op_timeout: float = 120.0, render_timeout: float = 900.0):
        self.cli, self.op_timeout, self.render_timeout = cli, op_timeout, render_timeout

    def discover(self) -> Capabilities:
        with MCPClient([self.cli, "mcp"], "effectcraft", timeout=30) as c:
            cmds = c.call("command_list")
            ids = {x["id"] for x in (cmds if isinstance(cmds, list) else cmds.get("commands", []))}
            return Capabilities(version=str(c.server_info.get("version")), tools=sorted(c.tools),
                                missing_tools=sorted(REQUIRED_TOOLS - set(c.tools)), missing_commands=sorted(REQUIRED_COMMANDS - ids))

    def session(self) -> "Session":
        return Session(self)

    def render(self, project: Path, comp: str, out: Path, width: int, height: int, fps: float, duration: float,
               ffprobe: str = "ffprobe", retries: int = 1) -> VideoFacts:
        """Render an .ecproj composition to H.264 MP4 and verify the file against the plan. Rendering is idempotent for a
        given project file, so one retry is safe for transient failures (e.g. process killed)."""
        out.parent.mkdir(parents=True, exist_ok=True)
        last = None
        for attempt in range(retries + 1):
            if out.exists():
                out.unlink()
            t = time.time()
            try:
                r = subprocess.run([self.cli, "render", "--comp", comp, "--out", str(out), "--format", "h264", "--audio", "off", str(project)],
                                   capture_output=True, text=True, timeout=self.render_timeout)
            except subprocess.TimeoutExpired:
                last = EngineError(f"EffectCraft render exceeded {self.render_timeout:.0f}s and was stopped. Try a lower preview resolution.", retryable=True)
                continue
            if r.returncode != 0:
                last = EngineError(f"EffectCraft render failed (exit {r.returncode}): {(r.stderr or r.stdout).strip()[-500:]}", retryable=True)
                continue
            log.info("rendered %s in %.1fs", out.name, time.time() - t)
            return verify_video(out, width, height, fps, duration, ffprobe, expect_audio=False)
        raise last  # type: ignore[misc]

    def render_frame(self, project: Path, comp: str, t: float, out_png: Path) -> Path:
        out_png.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run([self.cli, "render-frame", "--comp", comp, "--time", f"{t:.3f}", "--out", str(out_png), str(project)],
                           capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not out_png.is_file():
            raise EngineError(f"EffectCraft frame render failed: {(r.stderr or r.stdout).strip()[-300:]}")
        return out_png


class Session:
    """One headless editing session = one in-memory project. Not reusable after close()."""
    def __init__(self, adapter: EffectCraftAdapter):
        self.a = adapter
        self.c = MCPClient([adapter.cli, "mcp"], "effectcraft", timeout=adapter.op_timeout)

    def __enter__(self): self.c.start(); return self
    def __exit__(self, *x): self.c.close()

    def new_comp(self, name: str, width: int, height: int, fps: float, duration: float, background: str) -> int:
        r = self.c.call("execute_command", id="comp.new", params={"name": name, "width": width, "height": height, "frameRate": fps,
                                                                 "duration": duration, "background": background})
        return r["comp"]

    def batch(self, steps: list[dict], label: str = "AIVS") -> list[dict]:
        if not steps:
            return []
        return self.c.call("batch", steps=steps, label=label)["results"]

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        r = self.c.call("save_project", path=str(path))
        if not path.is_file() or path.stat().st_size == 0:
            raise EngineError(f"EffectCraft reported saving but {path} is missing.")
        return path

    def comp_info(self, comp) -> dict:
        return self.c.call("get_comp", comp=comp)
