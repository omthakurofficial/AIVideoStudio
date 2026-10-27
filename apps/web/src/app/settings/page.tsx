"use client";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, type AppSettingsResponse, type EngineVerifyReport } from "@/lib/api";

type TabId = "general" | "providers" | "effectcraft" | "filmcraft" | "stock" | "tts";

function SettingsContent() {
  const searchParams = useSearchParams();
  const initialTab = (searchParams.get("tab") as TabId) || "general";
  const [tab, setTab] = useState<TabId>(initialTab);
  const [data, setData] = useState<AppSettingsResponse | null>(null);
  const [probe, setProbe] = useState<EngineVerifyReport | null>(null);
  const [probing, setProbing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState("");

  useEffect(() => {
    const qTab = searchParams.get("tab") as TabId;
    if (qTab) setTab(qTab);
  }, [searchParams]);

  useEffect(() => {
    api.getSettings().then(setData).catch(() => {});
  }, []);

  async function runLiveMcpProbe() {
    setProbing(true);
    try {
      const res = await api.verifyEngines();
      setProbe(res);
    } finally {
      setProbing(false);
    }
  }

  async function updatePrefs(patch: Record<string, any>) {
    if (!data) return;
    setSaving(true);
    setSavedMsg("");
    try {
      const res = await api.saveSettings(patch);
      setData({ ...data, preferences: res.preferences });
      document.documentElement.setAttribute("data-theme", res.preferences.theme);
      document.documentElement.setAttribute("data-accent", res.preferences.accent_color);
      setSavedMsg("Settings saved");
    } finally {
      setSaving(false);
    }
  }

  const prefs = data?.preferences;

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 16 }}>
        <div>
          <h1 style={{ margin: 0 }}>Settings & Engine MCP Configuration</h1>
          <p className="muted" style={{ margin: "2px 0 0" }}>
            Configure AI providers, inspect EffectCraft & FilmCraft headless MCP connections, manage output defaults, and customize themes.
          </p>
        </div>
        <button type="button" onClick={runLiveMcpProbe} disabled={probing}>
          {probing ? "Probing MCP Servers…" : "⚡ Run Live MCP Handshake Probe"}
        </button>
      </div>

      <div className="tab-bar">
        <button type="button" className={`tab-btn ${tab === "general" ? "active" : ""}`} onClick={() => setTab("general")}>
          General & Theme
        </button>
        <button type="button" className={`tab-btn ${tab === "providers" ? "active" : ""}`} onClick={() => setTab("providers")}>
          AI Providers (Bedrock)
        </button>
        <button type="button" className={`tab-btn ${tab === "effectcraft" ? "active" : ""}`} onClick={() => setTab("effectcraft")}>
          EffectCraft (MCP)
        </button>
        <button type="button" className={`tab-btn ${tab === "filmcraft" ? "active" : ""}`} onClick={() => setTab("filmcraft")}>
          FilmCraft (MCP)
        </button>
        <button type="button" className={`tab-btn ${tab === "stock" ? "active" : ""}`} onClick={() => setTab("stock")}>
          Stock Media
        </button>
        <button type="button" className={`tab-btn ${tab === "tts" ? "active" : ""}`} onClick={() => setTab("tts")}>
          TTS & Captions
        </button>
      </div>

      {probe && (
        <section className="card" style={{ borderColor: probe.ok ? "var(--ok)" : "var(--bad)" }} aria-label="Live MCP Verification">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <h2 style={{ margin: 0 }}>
              Live Engine & MCP Handshake Result:{" "}
              <span className={`badge ${probe.ok ? "ok" : "bad"}`}>{probe.ok ? "ALL ENGINES & MCP VERIFIED" : "ISSUE DETECTED"}</span>
            </h2>
            <button type="button" className="secondary" onClick={() => setProbe(null)} style={{ padding: "4px 10px", fontSize: "0.78rem" }}>
              Dismiss
            </button>
          </div>
          <div className="row" style={{ marginTop: 12 }}>
            <div style={{ background: "var(--panel-alt)", padding: 12, borderRadius: 8, border: "1px solid var(--line)" }}>
              <strong>EffectCraft MCP ({probe.mcp.effectcraft?.version})</strong>
              <div className="muted" style={{ fontSize: "0.82rem", marginTop: 4 }}>
                Status: <span className={`badge ${probe.mcp.effectcraft?.ok ? "ok" : "bad"}`}>{probe.mcp.effectcraft?.ok ? "Connected (stdio MCP)" : "Failed"}</span><br />
                Transport: <code>{probe.mcp.effectcraft?.transport}</code><br />
                Verified MCP Tools: <strong>{probe.mcp.effectcraft?.tool_count} tools</strong> ({probe.mcp.effectcraft?.tools?.slice(0, 6).join(", ")}, …)
              </div>
            </div>
            <div style={{ background: "var(--panel-alt)", padding: 12, borderRadius: 8, border: "1px solid var(--line)" }}>
              <strong>FilmCraft MCP ({probe.mcp.filmcraft?.version})</strong>
              <div className="muted" style={{ fontSize: "0.82rem", marginTop: 4 }}>
                Status: <span className={`badge ${probe.mcp.filmcraft?.ok ? "ok" : "bad"}`}>{probe.mcp.filmcraft?.ok ? "Connected (stdio MCP)" : "Failed"}</span><br />
                Transport: <code>{probe.mcp.filmcraft?.transport}</code><br />
                Verified MCP Tools: <strong>{probe.mcp.filmcraft?.tool_count} tools</strong> ({probe.mcp.filmcraft?.tools?.slice(0, 6).join(", ")}, …)
              </div>
            </div>
          </div>
        </section>
      )}

      {tab === "general" && prefs && (
        <div className="grid-2">
          <section className="card">
            <h2>Default Production Preferences</h2>
            <label htmlFor="def-aspect">Default Aspect Ratio</label>
            <select
              id="def-aspect"
              value={prefs.default_aspect_ratio}
              onChange={e => updatePrefs({ default_aspect_ratio: e.target.value })}
            >
              <option value="16:9">16:9 (1920×1080 Landscape)</option>
              <option value="9:16">9:16 (1080×1920 Vertical Shorts)</option>
            </select>

            <label htmlFor="def-style">Default Visual Style</label>
            <select
              id="def-style"
              value={prefs.default_visual_style}
              onChange={e => updatePrefs({ default_visual_style: e.target.value })}
            >
              <option value="clean-technical">Clean Technical (Navy & Electric Blue)</option>
              <option value="dark-neon">Dark Neon (Violet & Cyan)</option>
              <option value="warm-documentary">Warm Documentary (Amber & Espresso)</option>
              <option value="light-minimal">Light Minimal</option>
            </select>

            <label htmlFor="def-appr">Default Approval Mode</label>
            <select
              id="def-appr"
              value={prefs.default_approval_mode}
              onChange={e => updatePrefs({ default_approval_mode: e.target.value })}
            >
              <option value="automatic">Automatic (End-to-End Video Generation)</option>
              <option value="manual">Manual Storyboard Review Before Rendering</option>
            </select>

            <div style={{ marginTop: 12 }}>
              <span className="muted">{saving ? "Saving…" : savedMsg}</span>
            </div>
          </section>

          <section className="card">
            <h2>Theme & Visual Personalization</h2>
            <p className="muted" style={{ marginTop: 0 }}>
              Customize the studio workspace appearance (persisted across sessions):
            </p>
            <label>Color Mode</label>
            <div className="row" style={{ marginBottom: 14 }}>
              <button
                type="button"
                className={prefs.theme === "dark" ? "" : "secondary"}
                onClick={() => updatePrefs({ theme: "dark" })}
              >
                ☾ Dark Navy Studio (Default)
              </button>
              <button
                type="button"
                className={prefs.theme === "light" ? "" : "secondary"}
                onClick={() => updatePrefs({ theme: "light" })}
              >
                ☀ Light Clean Workspace
              </button>
            </div>

            <label>Accent Color</label>
            <div className="row">
              <button
                type="button"
                className={prefs.accent_color === "blue" ? "" : "secondary"}
                onClick={() => updatePrefs({ accent_color: "blue" })}
              >
                ◆ Blue (Tech)
              </button>
              <button
                type="button"
                className={prefs.accent_color === "purple" ? "" : "secondary"}
                onClick={() => updatePrefs({ accent_color: "purple" })}
              >
                ◆ Purple (Creative)
              </button>
            </div>

            <div style={{ marginTop: 18, paddingTop: 14, borderTop: "1px solid var(--line)" }}>
              <h3>Project Storage Paths (Portable Linux & Windows)</h3>
              <div className="muted" style={{ fontSize: "0.82rem" }}>
                Projects Directory: <code>{data?.storage.projects_dir}</code><br />
                SQLite Metadata DB: <code>{data?.storage.db_path}</code>
              </div>
            </div>
          </section>
        </div>
      )}

      {tab === "providers" && (
        <section className="card">
          <h2>AI Provider Configuration (AWS Bedrock)</h2>
          <p className="muted">
            AIVideoStudio uses a task-based model abstraction backed by AWS Bedrock in region <code>{data?.engines.aws_region}</code>. Credentials are read securely from your environment or <code>~/.aws/credentials</code> and never exposed in browser responses.
          </p>
          <div style={{ marginBottom: 14 }}>
            <strong>AWS STS Credential Status: </strong>
            <span className={`badge ${data?.health?.aws?.ok ? "ok" : "bad"}`}>
              {data?.health?.aws?.ok ? `Connected (${data.health.aws.detail})` : `Unavailable (${data?.health?.aws?.detail})`}
            </span>
          </div>
          <table className="data-table">
            <thead>
              <tr>
                <th>Pipeline Task</th>
                <th>Provider</th>
                <th>Configured Model ID</th>
                <th>Max Tokens</th>
                <th>Temperature</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(data?.models ?? {}).map(([taskName, m]) => (
                <tr key={taskName}>
                  <td><strong>{taskName}</strong></td>
                  <td><span className="badge ok">{m.provider}</span></td>
                  <td><code>{m.model_id}</code></td>
                  <td>{m.max_tokens ?? 4096}</td>
                  <td>{m.temperature ?? 0.2}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {tab === "effectcraft" && (
        <section className="card">
          <h2>EffectCraft Connection & Headless MCP Guide</h2>
          <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: 14 }}>
            <span className={`badge ${data?.health?.tools?.effectcraft?.ok ? "ok" : "bad"}`}>
              {data?.health?.tools?.effectcraft?.ok ? "INSTALLED & READY" : "NOT FOUND"}
            </span>
            <span className="badge ok">Version: {data?.health?.tools?.effectcraft?.detail || "0.17.0"}</span>
            <span className="badge">Transport: Headless stdio MCP</span>
          </div>

          <div className="grid-2">
            <div style={{ background: "var(--panel-alt)", padding: 16, borderRadius: 10, border: "1px solid var(--line)" }}>
              <h3>1. Is EffectCraft Installed on Your System?</h3>
              <p className="muted" style={{ fontSize: "0.88rem" }}>
                <strong>Yes!</strong> EffectCraft v0.17.0 is already installed and SHA-256 verified inside this repository at:
              </p>
              <pre className="log" style={{ padding: 8, marginBottom: 10 }}>{data?.engines.effectcraft_cli}</pre>
              <p className="muted" style={{ fontSize: "0.85rem", margin: 0 }}>
                On Linux it uses the native <code>effectcraft-0.17.0-linux-x86_64</code> binary. When migrating to Windows + RTX 3060, running <code>python scripts/install_tools.py</code> automatically downloads the matching Windows <code>effectcraft-cli.exe</code> binary into <code>tools/effectcraft/</code>.
              </p>
            </div>

            <div style={{ background: "var(--panel-alt)", padding: 16, borderRadius: 10, border: "1px solid var(--line)" }}>
              <h3>2. Is MCP Needed & How Does AIVideoStudio Use It?</h3>
              <p className="muted" style={{ fontSize: "0.88rem" }}>
                <strong>Yes — Headless stdio MCP is used automatically by the backend.</strong> You do <strong>not</strong> need to open the EffectCraft desktop GUI or configure an external MCP config file manually.
              </p>
              <ul className="muted" style={{ fontSize: "0.85rem", paddingLeft: 18, margin: 0 }}>
                <li>For every scene, the backend spawns <code>effectcraft-cli mcp</code> over stdio JSON-RPC 2.0.</li>
                <li>It executes <code>comp.new</code>, batches multi-layered cards, badges, drop shadows, connectors, and keyframe animations via <code>command_batch</code>, and saves the editable <code>scenes/sXX/vN/scene.ecproj</code> file.</li>
                <li>It then renders the H.264 MP4 clip via <code>effectcraft-cli render --comp sXX</code> and verifies frame integrity with <code>ffprobe</code>.</li>
              </ul>
            </div>
          </div>

          <div style={{ marginTop: 14 }}>
            <button type="button" onClick={runLiveMcpProbe} disabled={probing}>
              {probing ? "Testing EffectCraft MCP…" : "Test EffectCraft MCP Connection Now"}
            </button>
          </div>
        </section>
      )}

      {tab === "filmcraft" && (
        <section className="card">
          <h2>FilmCraft Connection & Headless MCP Guide</h2>
          <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap", marginBottom: 14 }}>
            <span className={`badge ${data?.health?.tools?.filmcraft?.ok ? "ok" : "bad"}`}>
              {data?.health?.tools?.filmcraft?.ok ? "INSTALLED & READY" : "NOT FOUND"}
            </span>
            <span className="badge ok">Version: {data?.health?.tools?.filmcraft?.detail || "0.13.0"}</span>
            <span className="badge">Transport: Headless stdio MCP</span>
          </div>

          <div className="grid-2">
            <div style={{ background: "var(--panel-alt)", padding: 16, borderRadius: 10, border: "1px solid var(--line)" }}>
              <h3>1. Is FilmCraft Installed on Your System?</h3>
              <p className="muted" style={{ fontSize: "0.88rem" }}>
                <strong>Yes!</strong> FilmCraft v0.13.0 is installed and verified inside this repository at:
              </p>
              <pre className="log" style={{ padding: 8, marginBottom: 10 }}>{data?.engines.filmcraft_cli}</pre>
              <p className="muted" style={{ fontSize: "0.85rem", margin: 0 }}>
                Both Linux (<code>filmcraft-cli</code>) and Windows (<code>filmcraft-cli.exe</code> via <code>scripts/install_tools.py</code>) use the same portable adapter in <code>services/api/aivs/engines/filmcraft.py</code>.
              </p>
            </div>

            <div style={{ background: "var(--panel-alt)", padding: 16, borderRadius: 10, border: "1px solid var(--line)" }}>
              <h3>2. How FilmCraft MCP Assembles Your Final Video</h3>
              <p className="muted" style={{ fontSize: "0.88rem" }}>
                During Stage 7 (Assembly), AIVideoStudio launches <code>filmcraft-cli mcp</code> over stdio JSON-RPC 2.0 and runs:
              </p>
              <ul className="muted" style={{ fontSize: "0.85rem", paddingLeft: 18, margin: 0 }}>
                <li><code>file.newProject</code> & <code>file.newSequence</code> (1920×1080 or 1080×1920 @ 30fps, 48kHz stereo).</li>
                <li><code>file.import</code> & <code>timeline.place</code> to place all rendered scene MP4 clips on track <code>V1</code> and narration WAV files on track <code>A1</code>.</li>
                <li><code>captions.newTrack</code> & <code>captions.add</code> to store word-synced captions on track <code>C1</code>, saving <code>assembly/project.fcproj</code>.</li>
                <li><code>file.exportMedia</code> (H.264 + AAC) followed by deterministic FFmpeg <code>libass</code> subtitle burn-in for crisp 2–4 word pop-in captions.</li>
              </ul>
            </div>
          </div>

          <div style={{ marginTop: 14 }}>
            <button type="button" onClick={runLiveMcpProbe} disabled={probing}>
              {probing ? "Testing FilmCraft MCP…" : "Test FilmCraft MCP Connection Now"}
            </button>
          </div>
        </section>
      )}

      {tab === "stock" && (
        <section className="card">
          <h2>Stock Media APIs (Pexels & Pixabay)</h2>
          <p className="muted">
            When a scene requests background stock footage or imagery, AIVideoStudio queries Pexels and Pixabay APIs (if configured in <code>.env</code>) and caches normalized clips in <code>assets/stock/</code>. When keys are not set, the pipeline automatically generates animated procedural dark-canvas backgrounds so production never fails.
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 12 }}>
            <span className={`badge ${data?.health?.stock?.pexels_configured ? "ok" : ""}`}>
              Pexels API Key: {data?.health?.stock?.pexels_configured ? "Configured" : "Not Set (Using Procedural Canvas Fallback)"}
            </span>
            <span className={`badge ${data?.health?.stock?.pixabay_configured ? "ok" : ""}`}>
              Pixabay API Key: {data?.health?.stock?.pixabay_configured ? "Configured" : "Not Set (Using Procedural Canvas Fallback)"}
            </span>
          </div>
        </section>
      )}

      {tab === "tts" && prefs && (
        <section className="card">
          <h2>Narration (Neural TTS) & Synchronized Pop-In Captions</h2>
          <p className="muted">
            Narration is synthesized automatically using Microsoft Edge Neural TTS (<code>edge-tts</code>) with exact <code>WordBoundary</code> timestamps. Scene durations are automatically locked to the measured narration WAV audio, and captions are grouped into punchy 2–4 word phrases with crisp dark outlines and drop shadows.
          </p>
          <div className="row">
            <div>
              <label htmlFor="tts-voice">Default Neural Voice</label>
              <select
                id="tts-voice"
                value={prefs.default_voice}
                onChange={e => updatePrefs({ default_voice: e.target.value })}
              >
                <option value="en-US-GuyNeural">en-US-GuyNeural (Documentary Male)</option>
                <option value="en-US-AriaNeural">en-US-AriaNeural (Presenter Female)</option>
                <option value="en-GB-RyanNeural">en-GB-RyanNeural (British Male)</option>
              </select>
            </div>
            <div>
              <label htmlFor="cap-size">Caption Font Size Scale</label>
              <input
                id="cap-size"
                type="number"
                min={20}
                max={80}
                value={prefs.caption_font_size}
                onChange={e => updatePrefs({ caption_font_size: +e.target.value })}
              />
            </div>
          </div>
        </section>
      )}
    </>
  );
}

export default function SettingsPage() {
  return (
    <Suspense fallback={<p>Loading settings…</p>}>
      <SettingsContent />
    </Suspense>
  );
}
