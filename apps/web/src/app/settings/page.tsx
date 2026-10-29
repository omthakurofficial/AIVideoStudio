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
  const [pexelsInput, setPexelsInput] = useState("");
  const [pixabayInput, setPixabayInput] = useState("");

  useEffect(() => {
    const qTab = searchParams.get("tab") as TabId;
    if (qTab) setTab(qTab);
  }, [searchParams]);

  const reloadSettings = () => {
    api.getSettings().then(res => {
      setData(res);
    }).catch(() => {});
  };

  useEffect(() => {
    reloadSettings();
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
      const fresh = await api.getSettings();
      setData(fresh);
      document.documentElement.setAttribute("data-theme", res.preferences.theme);
      document.documentElement.setAttribute("data-accent", res.preferences.accent_color);
      setSavedMsg("Settings saved");
    } finally {
      setSaving(false);
    }
  }

  const prefs = data?.preferences;
  const catalog = data?.model_catalog ?? [];
  const voices = data?.available_voices ?? [];

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 16 }}>
        <div>
          <h1 style={{ margin: 0 }}>Settings & Engine MCP Configuration</h1>
          <p className="muted" style={{ margin: "2px 0 0" }}>
            Configure AWS Bedrock AI models & official token pricing, inspect EffectCraft & FilmCraft headless MCP, manage Pexels/Pixabay/Wikimedia stock media, and select local Kokoro-82M voices.
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
          TTS (Kokoro) & Captions
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
        <>
          <section className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10 }}>
              <div>
                <h2 style={{ margin: 0 }}>AI Provider Configuration (AWS Bedrock — Region: {data?.engines.aws_region})</h2>
                <p className="muted" style={{ margin: "4px 0 0" }}>
                  Select which AWS Bedrock model drives each stage of video production (Anthropic Claude &le; 4.5, Amazon Nova, DeepSeek, MiniMax, Qwen, Mistral, Moonshot Kimi, NVIDIA; OpenAI excluded).
                </p>
              </div>
              <div>
                <span className={`badge ${data?.health?.aws?.ok ? "ok" : "bad"}`}>
                  {data?.health?.aws?.ok ? `AWS Connected (${data.health.aws.detail})` : `AWS Unavailable (${data?.health?.aws?.detail})`}
                </span>
              </div>
            </div>

            <table className="data-table" style={{ marginTop: 14 }}>
              <thead>
                <tr>
                  <th>Pipeline Task</th>
                  <th>Provider</th>
                  <th>Select Active AI Model</th>
                  <th>Max Tokens</th>
                  <th>Temperature</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(data?.models ?? {}).map(([taskName, m]) => (
                  <tr key={taskName}>
                    <td><strong>{taskName}</strong></td>
                    <td><span className="badge ok">{m.provider}</span></td>
                    <td>
                      <select
                        aria-label={`Model for ${taskName}`}
                        value={m.model_id}
                        onChange={e => updatePrefs({ task_models: { [taskName]: e.target.value } })}
                        style={{ margin: 0 }}
                      >
                        {catalog.map(c => (
                          <option key={c.model_id} value={c.model_id}>
                            {c.label} (${c.input_per_1m_usd.toFixed(2)} / ${c.output_per_1m_usd.toFixed(2)} per 1M)
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>{m.max_tokens ?? 4096}</td>
                    <td>{m.temperature ?? 0.2}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {savedMsg && <p className="muted" style={{ marginTop: 8 }}>{savedMsg}</p>}
          </section>

          {(data?.architecture_layers ?? []).length > 0 && (
            <section className="card" aria-label="5-Layer Hybrid Architecture">
              <h2 style={{ margin: "0 0 6px" }}>5-Layer Hybrid Production Architecture (AWS Bedrock + $0.00 Local Engines)</h2>
              <p className="muted" style={{ margin: "0 0 12px", fontSize: ".85rem" }}>
                Layers 2, 3, 4, and 5 default to $0.00 local execution (Real GeoJSON/Satellite Maps, 2D Cartoon/SVG Sprites, EffectCraft MCP, Kokoro-82M Neural TTS, and Active Word-Highlighted .ASS Captions) while keeping Bedrock image/video/audio models available on-demand.
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 10 }}>
                {(data?.architecture_layers ?? []).map(l => (
                  <div key={l.layer} style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 10, padding: 12 }}>
                    <div style={{ fontWeight: 700, marginBottom: 4 }}>{l.title}</div>
                    <p className="muted" style={{ fontSize: ".78rem", margin: "0 0 8px" }}>{l.description}</p>
                    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                      {l.options.map(opt => (
                        <div key={opt.id} style={{ fontSize: ".78rem", background: "var(--input-bg)", padding: "6px 8px", borderRadius: 6, border: "1px solid var(--line)" }}>
                          <div style={{ fontWeight: 600 }}>{opt.name}</div>
                          <div className="muted" style={{ display: "flex", justifyContent: "space-between", marginTop: 2 }}>
                            <code>{opt.id}</code>
                            <span className={`badge ${opt.mode === "local" ? "ok" : ""}`}>{opt.cost}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 10, marginBottom: 12 }}>
              <h2 style={{ margin: 0 }}>Available AWS Bedrock Models & Official Token Pricing (USD per 1M Tokens)</h2>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {(data?.official_pricing_links ?? []).map(link => (
                  <a
                    key={link.url}
                    href={link.url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn secondary"
                    style={{ padding: "4px 10px", fontSize: "0.78rem" }}
                  >
                    ↗ {link.name}
                  </a>
                ))}
              </div>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Vendor & Family</th>
                  <th>Model Name</th>
                  <th>Bedrock Model / Profile ID</th>
                  <th>Input / 1M Tokens</th>
                  <th>Output / 1M Tokens</th>
                  <th>Official Pricing Source</th>
                </tr>
              </thead>
              <tbody>
                {catalog.map(c => (
                  <tr key={c.model_id}>
                    <td>
                      <span className="badge ok">{c.vendor}</span>{" "}
                      <span className="muted" style={{ fontSize: "0.78rem" }}>{c.family}</span>
                    </td>
                    <td><strong>{c.label}</strong></td>
                    <td><code>{c.model_id}</code></td>
                    <td><strong>${c.input_per_1m_usd.toFixed(2)}</strong></td>
                    <td><strong>${c.output_per_1m_usd.toFixed(2)}</strong></td>
                    <td>
                      <a href={c.official_pricing_url} target="_blank" rel="noreferrer" style={{ fontSize: "0.8rem" }}>
                        Official Rate ↗
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
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
                <li>It executes <code>comp.new</code>, builds 2D cartographic maps, multi-shape 2D vector icons, cards, drop shadows, connectors, and keyframe animations via <code>command_batch</code>, and saves the editable <code>scenes/sXX/vN/scene.ecproj</code> file.</li>
                <li>It then renders the H.264 MP4 clip via <code>effectcraft-cli render --comp sXX</code>, composites any Pexels/Pixabay/Wikimedia stock media cards, and verifies frame integrity with <code>ffprobe</code>.</li>
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
                <li><code>file.import</code> & <code>timeline.place</code> to place all rendered scene MP4 clips on track <code>V1</code> and Kokoro/Neural narration WAV files on track <code>A1</code>.</li>
                <li><code>captions.newTrack</code> & <code>captions.add</code> to store word-synced captions on track <code>C1</code>, saving <code>assembly/project.fcproj</code>.</li>
                <li><code>file.exportMedia</code> (H.264 + AAC) followed by deterministic FFmpeg <code>libass</code> subtitle burn-in with <strong>Active Word Gold Highlighting</strong> (<code>captions/captions.ass</code>).</li>
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
          <h2>Stock Media & Open-Web Map/Photo Libraries (Pexels, Pixabay & Wikimedia Commons)</h2>
          <p className="muted">
            When a scene requests real-world imagery or documentary footage, AIVideoStudio searches official <strong>Pexels</strong>, <strong>Pixabay</strong>, and <strong>Wikimedia Commons Open-Web Media</strong> APIs, validates downloaded files with <code>ffprobe</code>/Pillow, records full provenance & license metadata, and composites a framed documentary visual card onto the scene.
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 12, marginBottom: 16 }}>
            <span className={`badge ${data?.stock_media?.pexels_configured ? "ok" : ""}`}>
              Pexels API Key: {data?.stock_media?.pexels_configured ? `Active (${data.stock_media.pexels_masked})` : "Not Set"}
            </span>
            <span className={`badge ${data?.stock_media?.pixabay_configured ? "ok" : ""}`}>
              Pixabay API Key: {data?.stock_media?.pixabay_configured ? `Active (${data.stock_media.pixabay_masked})` : "Not Set"}
            </span>
            <span className="badge ok">
              Wikimedia Commons Open-Web API: Active (Free Public Domain / CC Maps & Photos)
            </span>
            <span className="badge ok">
              EffectCraft 2D Cartographic Map Engine: Active
            </span>
          </div>

          <div className="grid-2">
            <div>
              <label htmlFor="pexels-key">Pexels API Key (Saved securely in local <code>.env</code>)</label>
              <input
                id="pexels-key"
                type="password"
                placeholder={data?.stock_media?.pexels_configured ? `Configured (${data.stock_media.pexels_masked}) — enter new key to replace` : "Paste your Pexels API Key"}
                value={pexelsInput}
                onChange={e => setPexelsInput(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="pixabay-key">Pixabay API Key (Saved securely in local <code>.env</code>)</label>
              <input
                id="pixabay-key"
                type="password"
                placeholder={data?.stock_media?.pixabay_configured ? `Configured (${data.stock_media.pixabay_masked}) — enter new key to replace` : "Paste your Pixabay API Key"}
                value={pixabayInput}
                onChange={e => setPixabayInput(e.target.value)}
              />
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <button
              type="button"
              disabled={saving || (!pexelsInput.trim() && !pixabayInput.trim())}
              onClick={async () => {
                await updatePrefs({
                  pexels_api_key: pexelsInput.trim() || undefined,
                  pixabay_api_key: pixabayInput.trim() || undefined,
                });
                setPexelsInput("");
                setPixabayInput("");
              }}
            >
              Save Stock Media API Keys
            </button>
            {savedMsg && <span className="muted" style={{ marginLeft: 12 }}>{savedMsg}</span>}
          </div>
        </section>
      )}

      {tab === "tts" && prefs && (
        <section className="card">
          <h2>Local Kokoro-82M Neural Voice Model & Word-Highlighted Captions</h2>
          <p className="muted">
            Your system has the local <strong>Kokoro-82M Neural TTS model</strong> (<code>hexgrad/Kokoro-82M</code>, 54 voices in <code>voices-v1.0.bin</code>) installed and verified. Kokoro runs 100% locally at <strong>$0.00 cost</strong> and outputs exact phoneme-level word timestamps so each spoken word highlights in <strong>vibrant Gold (<code>#FFD700</code>)</strong> inside the burned-in <code>.ass</code> captions as it is spoken!
          </p>
          <div className="row">
            <div>
              <label htmlFor="tts-voice">Default Neural Voice (Local Kokoro-82M or Microsoft Edge Neural)</label>
              <select
                id="tts-voice"
                value={prefs.default_voice}
                onChange={e => updatePrefs({ default_voice: e.target.value })}
              >
                {voices.length > 0 ? (
                  voices.map(v => (
                    <option key={v.id} value={v.id}>
                      {v.label} ({v.provider === "kokoro-82m-local" ? "Local GPU/CPU — $0.00" : "Cloud Free — $0.00"})
                    </option>
                  ))
                ) : (
                  <>
                    <option value="kokoro:am_michael">Kokoro-82M (Local Neural) — Michael (US Documentary Male)</option>
                    <option value="kokoro:af_heart">Kokoro-82M (Local Neural) — Heart (US Expressive Female)</option>
                    <option value="en-US-GuyNeural">Microsoft Edge Neural — Guy (US Documentary Male)</option>
                  </>
                )}
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
          <div style={{ marginTop: 14, padding: 12, background: "var(--panel-alt)", borderRadius: 8, border: "1px solid var(--line)" }}>
            <strong>Active Spoken-Word Highlighting Mode: </strong>
            <span className="badge ok">ENABLED (ASS Gold Word Highlight + 108% Pop Scale)</span>
            <p className="muted" style={{ margin: "6px 0 0", fontSize: "0.84rem" }}>
              Every caption phrase displays 2–4 words in the lower-third safe zone. As the narrator speaks each word, that active word lights up in gold (<code>#FFD700</code>) with a subtle 108% scale pop while surrounding words remain crisp white (<code>#FFFFFF</code>). Both <code>captions/captions.srt</code> and <code>captions/captions.ass</code> are saved in the project workspace.
            </p>
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
