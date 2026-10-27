"""Minimal stdio MCP probe: initialize + tools/list. Usage: mcp_probe.py <cmd> [args...]"""
import json, subprocess, sys, threading, queue

def main():
    p = subprocess.Popen(sys.argv[1:], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, bufsize=1)
    q = queue.Queue()
    threading.Thread(target=lambda: [q.put(l) for l in p.stdout], daemon=True).start()
    def send(m): p.stdin.write(json.dumps(m) + "\n"); p.stdin.flush()
    def recv(id_, t=30):
        while True:
            m = json.loads(q.get(timeout=t))
            if m.get("id") == id_: return m
    send({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}})
    init = recv(1); print("server:", json.dumps(init["result"].get("serverInfo")), "proto:", init["result"].get("protocolVersion"))
    send({"jsonrpc":"2.0","method":"notifications/initialized"})
    tools, cur, i = [], None, 2
    while True:
        params = {"cursor": cur} if cur else {}
        send({"jsonrpc":"2.0","id":i,"method":"tools/list","params":params}); r = recv(i)["result"]
        tools += r["tools"]; cur = r.get("nextCursor"); i += 1
        if not cur: break
    print("tool count:", len(tools))
    json.dump(tools, open("/tmp/tools_%s.json" % p.args[0].split("/")[-1], "w"), indent=1)
    for t in tools[:60]: print(" -", t["name"], "|", (t.get("description") or "")[:90].replace("\n"," "))
    p.terminate()
main()
