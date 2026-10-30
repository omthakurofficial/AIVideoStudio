"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  api,
  type V2NicheItem,
  type V2VoiceItem,
  type V2BedrockModelItem,
  type V2TokenTelemetry,
  type V2TemplateBlueprint,
  type V2SceneBlueprint,
} from "@/lib/api";

const DEFAULT_BEDROCK_MODELS: V2BedrockModelItem[] = [
  {
    id: "apac.anthropic.claude-3-5-sonnet-20241022-v2:0",
    name: "Claude 3.5 Sonnet v2",
    vendor: "Anthropic",
    badge: "🧠 Flagship Creative Director",
    input_cost_per_1m: 3.00,
    output_cost_per_1m: 15.00,
    speed: "Balanced",
    description: "Highest retention narrative pacing, viral psychological hooks, cinematic choreography"
  },
  {
    id: "apac.anthropic.claude-3-haiku-20240307-v1:0",
    name: "Claude 3 Haiku",
    vendor: "Anthropic",
    badge: "⚡ Ultra-Fast & 90% Cost Saving",
    input_cost_per_1m: 0.25,
    output_cost_per_1m: 1.25,
    speed: "Ultra Fast",
    description: "Sub-second response, ultra-low token cost ($0.0003/video), great for rapid iteration"
  },
  {
    id: "au.anthropic.claude-haiku-4-5-20251001-v1:0",
    name: "Claude Haiku 4.5",
    vendor: "Anthropic",
    badge: "🚀 Next-Gen Fast Reasoning",
    input_cost_per_1m: 1.00,
    output_cost_per_1m: 5.00,
    speed: "Very Fast",
    description: "State-of-the-art fast model with higher structured prompt precision"
  },
  {
    id: "apac.amazon.nova-pro-v1:0",
    name: "Amazon Nova Pro",
    vendor: "Amazon",
    badge: "🌐 Multimodal Cinematic Reasoning",
    input_cost_per_1m: 0.80,
    output_cost_per_1m: 3.20,
    speed: "Fast",
    description: "AWS native multimodal model tailored for complex scene choreography"
  },
  {
    id: "apac.amazon.nova-lite-v1:0",
    name: "Amazon Nova Lite",
    vendor: "Amazon",
    badge: "💰 Ultra-Economical (~$0.0001/video)",
    input_cost_per_1m: 0.06,
    output_cost_per_1m: 0.24,
    speed: "Lightning",
    description: "Lowest cost Bedrock model available, saves 98% on token spend"
  },
  {
    id: "deepseek.v3.2",
    name: "DeepSeek V3.2",
    vendor: "DeepSeek",
    badge: "🎯 Viral Retention & Data Logic",
    input_cost_per_1m: 0.58,
    output_cost_per_1m: 1.68,
    speed: "Fast",
    description: "Specialized in pattern interrupts, contrarian angles, and analytical breakdowns"
  },
  {
    id: "minimax.minimax-m2.5",
    name: "MiniMax M2.5",
    vendor: "MiniMax",
    badge: "✍️ Narrative Conversational Writer",
    input_cost_per_1m: 0.30,
    output_cost_per_1m: 1.20,
    speed: "Fast",
    description: "Natural human cadence, great for podcast and explainer storytelling"
  }
];

export default function V2StudioPage() {
  const [niches, setNiches] = useState<V2NicheItem[]>([]);
  const [voices, setVoices] = useState<V2VoiceItem[]>([]);
  const [models, setModels] = useState<V2BedrockModelItem[]>(DEFAULT_BEDROCK_MODELS);
  const [selectedNicheId, setSelectedNicheId] = useState<string>("youtube_growth");
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>("kokoro:am_michael");
  const [selectedModelId, setSelectedModelId] = useState<string>("apac.anthropic.claude-3-5-sonnet-20241022-v2:0");
  const [inputMode, setInputMode] = useState<"master" | "url_reference" | "manual">("master");

  // Format, Duration & Concept Fields
  const [topic, setTopic] = useState("");
  const [duration, setDuration] = useState<number>(60);
  const [aspect, setAspect] = useState<"9:16" | "16:9">("9:16");

  // URL Reference & Avatar Transform Mode
  const [referenceUrl, setReferenceUrl] = useState("");
  const [humanAvatarTransform, setHumanAvatarTransform] = useState("2d_cartoon");

  // Manual Mode Granular Placeholders
  const [hookPlaceholder, setHookPlaceholder] = useState("");
  const [problemPlaceholder, setProblemPlaceholder] = useState("");
  const [mechanismPlaceholder, setMechanismPlaceholder] = useState("");
  const [metricPlaceholder, setMetricPlaceholder] = useState("");
  const [brollSelection, setBrollSelection] = useState("");
  const [brandLogoUrl, setBrandLogoUrl] = useState("");

  // Result & Execution State
  const [busyScript, setBusyScript] = useState(false);
  const [busyAudio, setBusyAudio] = useState(false);
  const [renderingMp4, setRenderingMp4] = useState(false);
  const [renderedMp4Result, setRenderedMp4Result] = useState<{ mp4_file: string; filename: string; download_url: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [blueprint, setBlueprint] = useState<V2TemplateBlueprint | null>(null);
  const [activeInspectorTab, setActiveInspectorTab] = useState<"storyboard" | "player" | "html" | "prompt" | "audio" | "raw">("storyboard");
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [copiedHtml, setCopiedHtml] = useState(false);
  const [liveHtmlSrcDoc, setLiveHtmlSrcDoc] = useState<string>("");
  const [activeSceneIdx, setActiveSceneIdx] = useState<number>(0);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    api.v2Niches().then(res => {
      setNiches(res.niches);
      if (res.voices) setVoices(res.voices);
      if (res.models && res.models.length > 0) setModels(res.models);
      if (res.niches.length > 0) {
        setSelectedNicheId(res.niches[0].id);
        setTopic(res.niches[0].sample_topics[0]);
      }
    }).catch(err => {
      console.warn("Could not load v2 niches from backend API, using fallback", err);
    });
  }, []);

  const selectedNiche = niches.find(n => n.id === selectedNicheId) || niches[0];
  const selectedModel = models.find(m => m.id === selectedModelId) || models[0];

  function handleSelectNiche(n: V2NicheItem, sampleTopic?: string) {
    setSelectedNicheId(n.id);
    setAspect(n.default_aspect);
    if (sampleTopic) {
      setTopic(sampleTopic);
    } else if (n.sample_topics?.length > 0) {
      setTopic(n.sample_topics[0]);
    }
  }

  // STEP 1: Generate Master Script & Blueprint (Fast & Token Efficient)
  async function generateMasterScriptOnly() {
    let finalTopic = topic.trim();
    let customNotes: string | undefined = undefined;

    if (inputMode === "url_reference") {
      if (!referenceUrl.trim()) {
        setError("Please enter a reference URL (YouTube, Shorts, Reels, TikTok, PDF, or Deck link).");
        return;
      }
      finalTopic = topic.trim() || `Deconstructed Re-creation from: ${referenceUrl.trim()}`;
      customNotes = `Reference Analysis & Avatar Transformation:
- Source URL: ${referenceUrl.trim()}
- Presenter Avatar Style: ${humanAvatarTransform}
- Directive: Deconstruct reference video frame-by-frame: extract hook, retention drops, core punchlines. Re-synthesize narrative into chosen archetype (${selectedNiche?.name}), replace human presenter with animated ${humanAvatarTransform} avatar.`;
    } else if (inputMode === "manual") {
      if (!finalTopic) {
        setError("Please enter a topic or concept.");
        return;
      }
      customNotes = `Manual Placeholders:
- Hook: ${hookPlaceholder}
- Problem: ${problemPlaceholder}
- Mechanism: ${mechanismPlaceholder}
- Metric: ${metricPlaceholder}
- B-Roll / Layered Props: ${brollSelection}
- Brand Assets: ${brandLogoUrl}`;
    } else {
      if (!finalTopic) {
        setError("Please enter a topic or concept.");
        return;
      }
    }

    setBusyScript(true);
    setError(null);
    try {
      const res = await api.v2GenerateTemplate({
        topic: finalTopic,
        niche_id: selectedNicheId,
        target_duration_s: duration,
        aspect_ratio: aspect,
        mode: inputMode === "master" ? "master_auto" : (inputMode === "url_reference" ? "url_reference_remix" : "manual_placeholders"),
        voice_id: selectedVoiceId,
        model_id: selectedModelId,
        synthesize_audio: false, // Step 1: Script & Blueprint only!
        custom_instructions: customNotes,
      });
      setBlueprint(res);
      setActiveInspectorTab("storyboard");
    } catch (err) {
      setError((err as Error).message || "Master script generation failed.");
    } finally {
      setBusyScript(false);
    }
  }

  // STEP 2: Synthesize Voice Audio & Build Live Canvas Player
  async function synthesizeVoiceAndLivePlayer() {
    if (!topic.trim()) {
      setError("Please enter or generate a master topic first.");
      return;
    }
    setBusyAudio(true);
    setError(null);
    setRenderedMp4Result(null);
    try {
      const res = await api.v2SynthesizePlayer({
        topic: topic.trim(),
        niche_id: selectedNicheId,
        target_duration_s: duration,
        aspect_ratio: aspect,
        mode: inputMode === "master" ? "master_auto" : (inputMode === "url_reference" ? "url_reference_remix" : "manual_placeholders"),
        voice_id: selectedVoiceId,
        model_id: selectedModelId,
      });
      setBlueprint(res);
      if (res.standalone_html_code) {
        setLiveHtmlSrcDoc(res.standalone_html_code);
        setActiveInspectorTab("player");
      }
    } catch (err) {
      setError((err as Error).message || "Voice synthesis and player generation failed.");
    } finally {
      setBusyAudio(false);
    }
  }

  // STEP 3: Render Final Local MP4 Video
  async function renderFinalMp4() {
    if (!blueprint?.html_file || !blueprint?.master_wav) {
      setError("Please synthesize the live player (Step 2) before rendering MP4.");
      return;
    }
    setRenderingMp4(true);
    setError(null);
    try {
      const res = await api.v2RenderMp4({
        html_file: blueprint.html_file,
        master_wav: blueprint.master_wav,
        aspect_ratio: aspect
      });
      setRenderedMp4Result(res);
    } catch (err) {
      setError((err as Error).message || "MP4 rendering failed.");
    } finally {
      setRenderingMp4(false);
    }
  }

  function jumpToScene(sceneIdx: number, startSec: number) {
    setActiveSceneIdx(sceneIdx);
    if (iframeRef.current?.contentWindow) {
      try {
        (iframeRef.current.contentWindow as unknown as { seek: (t: number) => void }).seek(startSec);
      } catch (e) {
        console.warn("Could not seek player iframe", e);
      }
    }
  }

  function copyPromptToClipboard() {
    if (!blueprint?.portable_master_prompt) return;
    navigator.clipboard.writeText(blueprint.portable_master_prompt);
    setCopiedPrompt(true);
    setTimeout(() => setCopiedPrompt(false), 2500);
  }

  function copyHtmlToClipboard() {
    if (!blueprint?.standalone_html_code) return;
    navigator.clipboard.writeText(blueprint.standalone_html_code);
    setCopiedHtml(true);
    setTimeout(() => setCopiedHtml(false), 2500);
  }

  function downloadHtmlFile() {
    if (!blueprint?.standalone_html_code) return;
    const blob = new Blob([blueprint.standalone_html_code], { type: "text/html;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${selectedNicheId}_${duration}s_${aspect.replace(":", "x")}_player.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function downloadPromptFile() {
    if (!blueprint) return;
    const blob = new Blob([blueprint.portable_master_prompt], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${selectedNicheId}_${duration}s_${aspect.replace(":", "x")}_master_prompt.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div style={{ maxWidth: 1340, margin: "0 auto", paddingBottom: 60 }}>
      {/* Studio Header */}
      <div className="card" style={{
        background: "linear-gradient(135deg, rgba(20, 20, 32, 0.98) 0%, rgba(10, 10, 16, 0.99) 100%)",
        border: "1px solid rgba(255, 214, 10, 0.3)",
        boxShadow: "0 10px 40px rgba(0,0,0,0.6)",
        marginBottom: 20
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
              <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a", border: "1px solid #ffd60a" }}>
                V2 PRODUCTION STUDIO
              </span>
              <span className="badge ok">10 Top Earning Niches</span>
              <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", border: "1px solid #38bdf8" }}>
                Multi-Bedrock Engine
              </span>
              <span className="badge" style={{ background: "rgba(48, 209, 88, 0.15)", color: "#30d158", border: "1px solid #30d158" }}>
                Zero Token Waste
              </span>
            </div>
            <h1 style={{ margin: "4px 0", fontSize: "1.75rem", fontFamily: "var(--font-display, inherit)", letterSpacing: "0.02em" }}>
              AI Video Studio V2 · Live Play &amp; Blueprint Engine
            </h1>
            <p className="muted" style={{ margin: 0, fontSize: "0.92rem", maxWidth: 940 }}>
              Separated 3-step workflow: <strong>Step 1</strong> generates your master script with live token telemetry. <strong>Step 2</strong> synthesizes speech &amp; interactive live player. <strong>Step 3</strong> renders local MP4.
            </p>
          </div>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <button
              type="button"
              className="btn secondary"
              onClick={() => {
                if (selectedNiche?.sample_topics?.length > 0) {
                  setTopic(selectedNiche.sample_topics[Math.floor(Math.random() * selectedNiche.sample_topics.length)]);
                }
              }}
            >
              🎲 Random Niche Topic
            </button>
            <button
              type="button"
              className="btn"
              disabled={busyScript}
              onClick={generateMasterScriptOnly}
              style={{ background: "#ffd60a", color: "#000", fontWeight: 800 }}
            >
              {busyScript ? "Generating Script..." : "📝 Step 1: Generate Master Script"}
            </button>
            <button
              type="button"
              className="btn"
              disabled={busyAudio}
              onClick={synthesizeVoiceAndLivePlayer}
              style={{ background: "linear-gradient(135deg, #38bdf8 0%, #0284c7 100%)", color: "#fff", fontWeight: 800 }}
            >
              {busyAudio ? "Synthesizing Audio..." : "▶️ Step 2: Live Play Video"}
            </button>
          </div>
        </div>
      </div>

      {error && <div role="alert" className="error" style={{ marginBottom: 20 }}>{error}</div>}

      {/* Interactive Step-by-Step Production Pipeline Tracker */}
      <div className="card" style={{
        background: "rgba(14, 16, 26, 0.95)",
        border: "1px solid rgba(255,255,255,0.08)",
        padding: "12px 18px",
        marginBottom: 24
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          <strong style={{ fontSize: "0.86rem", color: "#e2e8f0" }}>🎯 Production Pipeline &amp; Guidance:</strong>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", fontSize: "0.78rem" }}>
            <span className="badge ok">1. Archetype: {selectedNiche?.badge}</span>
            <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8" }}>
              2. Ratio: {aspect} ({aspect === "9:16" ? "Shorts Safe" : "Widescreen"})
            </span>
            <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a" }}>
              3. Model: {selectedModel?.name}
            </span>
            <span className="badge">4. Mode: {inputMode === "master" ? "Master Concept" : (inputMode === "url_reference" ? "URL Analyzer" : "Granular Manual")}</span>
            <span className={`badge ${blueprint ? "ok" : ""}`}>
              {blueprint ? "✓ Script Ready" : "5. Script Pending"}
            </span>
            <span className={`badge ${blueprint?.has_audio ? "ok" : ""}`}>
              {blueprint?.has_audio ? "✓ Player Ready" : "6. Player Pending"}
            </span>
            <span className={`badge ${renderedMp4Result ? "ok" : ""}`}>
              {renderedMp4Result ? "✓ MP4 Rendered" : "7. MP4 Ready to Export"}
            </span>
          </div>
        </div>
      </div>

      {/* 1. Niche Archetypes Carousel / Grid */}
      <section className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.15rem" }}>1. Select Video Production Archetype (Top 10 YouTube &amp; Social Niches)</h2>
            <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.82rem" }}>
              Each archetype loads tailored visual choreography, color palettes, official icons, B-roll layers, and copyright-free scoring. Every niche supports <strong>both 16:9 Landscape &amp; 9:16 Shorts</strong>.
            </p>
          </div>
          {selectedNiche && (
            <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", border: "1px solid #38bdf8" }}>
              Active: {selectedNiche.name}
            </span>
          )}
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(230px, 1fr))",
          gap: 12
        }}>
          {niches.map(n => {
            const isSelected = n.id === selectedNicheId;
            return (
              <div
                key={n.id}
                onClick={() => handleSelectNiche(n)}
                style={{
                  background: isSelected ? "rgba(255, 214, 10, 0.08)" : "var(--panel-alt)",
                  border: isSelected ? "2px solid #ffd60a" : "1px solid var(--line)",
                  borderRadius: 10,
                  padding: 12,
                  cursor: "pointer",
                  transition: "all 0.18s ease",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between"
                }}
              >
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                    <span style={{ fontWeight: 700, fontSize: "0.86rem", color: isSelected ? "#ffd60a" : "var(--text)" }}>
                      {n.badge}
                    </span>
                    <span className="badge" style={{ fontSize: "0.68rem", padding: "2px 6px", background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8" }}>
                      Dual 16:9 &amp; 9:16
                    </span>
                  </div>
                  <div className="muted" style={{ fontSize: "0.74rem", marginBottom: 6 }}>
                    Inspired by: {n.reference_channels}
                  </div>
                  <p className="muted" style={{ fontSize: "0.76rem", margin: "0 0 10px", lineHeight: 1.35 }}>
                    {n.description}
                  </p>
                </div>

                <div style={{ display: "flex", gap: 6, flexWrap: "wrap", borderTop: "1px solid rgba(255,255,255,0.06)", paddingTop: 8 }}>
                  <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
                    <span style={{ width: 10, height: 10, borderRadius: "50%", background: n.colors.accent }} />
                    <span style={{ width: 10, height: 10, borderRadius: "50%", background: n.colors.secondary }} />
                    <span style={{ width: 10, height: 10, borderRadius: "50%", background: n.colors.highlight }} />
                  </div>
                  <button
                    type="button"
                    className="secondary"
                    style={{ fontSize: "0.72rem", padding: "3px 8px", marginLeft: "auto" }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectNiche(n, n.sample_topics[0]);
                    }}
                  >
                    Sample Topic →
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 2. Format, Bedrock Model, Audio & Duration Studio (Overhauled Spacious Layout) */}
      <section className="card" style={{ marginBottom: 24, background: "linear-gradient(180deg, var(--panel) 0%, rgba(14, 16, 26, 0.98) 100%)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.15rem" }}>2. Production Specs: Ratio, Bedrock Model, Voice &amp; Duration</h2>
            <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.82rem" }}>
              Configure your platform format, select from multi-cloud Bedrock models, choose authentic voice accents, and lock your pacing duration.
            </p>
          </div>
          <span className="badge ok" style={{ fontSize: "0.75rem" }}>
            ⚡ 100% Token Efficient
          </span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(310px, 1fr))", gap: 16 }}>
          {/* Card A: Target Aspect Ratio & Token Waste Prevention */}
          <div style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 10, padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <label style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                📐 Aspect Ratio &amp; Platform:
              </label>
              <span className="badge" style={{ fontSize: "0.68rem" }}>Single-Ratio Lock</span>
            </div>
            <p className="muted" style={{ fontSize: "0.74rem", margin: "0 0 10px" }}>
              Choose your exact platform target. Prompt tokens are strictly spent on <strong>one chosen ratio</strong> to prevent Bedrock token waste!
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <button
                type="button"
                className={`btn ${aspect === "9:16" ? "" : "secondary"}`}
                onClick={() => setAspect("9:16")}
                style={{
                  padding: "12px 10px",
                  textAlign: "center",
                  border: aspect === "9:16" ? "2px solid #ffd60a" : undefined
                }}
              >
                <div style={{ fontWeight: 800, fontSize: "0.92rem" }}>📱 9:16 Vertical</div>
                <div style={{ fontSize: "0.7rem", opacity: 0.85, marginTop: 2 }}>Shorts · Reels · TikTok</div>
                <div style={{ fontSize: "0.66rem", color: "#38bdf8", marginTop: 4 }}>Safe Zones (280/440px)</div>
              </button>
              <button
                type="button"
                className={`btn ${aspect === "16:9" ? "" : "secondary"}`}
                onClick={() => setAspect("16:9")}
                style={{
                  padding: "12px 10px",
                  textAlign: "center",
                  border: aspect === "16:9" ? "2px solid #ffd60a" : undefined
                }}
              >
                <div style={{ fontWeight: 800, fontSize: "0.92rem" }}>🖥️ 16:9 Landscape</div>
                <div style={{ fontSize: "0.7rem", opacity: 0.85, marginTop: 2 }}>YouTube · Facebook · TV</div>
                <div style={{ fontSize: "0.66rem", color: "#30d158", marginTop: 4 }}>Full 1920x1080 Framing</div>
              </button>
            </div>
          </div>

          {/* Card B: AWS Bedrock Model Selection & Token Budget */}
          <div style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 10, padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <label style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                🤖 AWS Bedrock Model:
              </label>
              <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", fontSize: "0.68rem" }}>
                {selectedModel?.vendor}
              </span>
            </div>
            <select
              value={selectedModelId}
              onChange={e => setSelectedModelId(e.target.value)}
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: 8,
                border: "1px solid var(--line)",
                background: "var(--panel)",
                color: "var(--text)",
                fontSize: "0.84rem",
                marginBottom: 8
              }}
            >
              {models.map(m => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.badge}) — ${m.input_cost_per_1m.toFixed(2)} / ${m.output_cost_per_1m.toFixed(2)} per 1M
                </option>
              ))}
            </select>
            <div style={{
              background: "rgba(0,0,0,0.35)",
              borderRadius: 6,
              padding: "8px 10px",
              fontSize: "0.73rem",
              lineHeight: 1.4
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", color: "#ffd60a", fontWeight: 700 }}>
                <span>{selectedModel?.badge}</span>
                <span>Speed: {selectedModel?.speed}</span>
              </div>
              <div className="muted" style={{ marginTop: 2 }}>{selectedModel?.description}</div>
            </div>
          </div>

          {/* Card C: Natural Neural Voice Selection ($0.00 Free TTS) */}
          <div style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 10, padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <label style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                🎙️ Voiceover Accent &amp; Gender:
              </label>
              <span className="badge ok" style={{ fontSize: "0.68rem" }}>$0.00 Free TTS</span>
            </div>
            <select
              value={selectedVoiceId}
              onChange={e => setSelectedVoiceId(e.target.value)}
              style={{
                width: "100%",
                padding: "10px",
                borderRadius: 8,
                border: "1px solid var(--line)",
                background: "var(--panel)",
                color: "var(--text)",
                fontSize: "0.84rem",
                marginBottom: 8
              }}
            >
              <optgroup label="🇺🇸 US Kokoro Local Voices ($0.00)">
                <option value="kokoro:am_michael">Michael (US Deep Documentary Male)</option>
                <option value="kokoro:af_heart">Heart (US Warm Expressive Female)</option>
                <option value="kokoro:af_bella">Bella (US Storyteller Female)</option>
                <option value="kokoro:am_adam">Adam (US Gritty Motivation Male)</option>
              </optgroup>
              <optgroup label="🇬🇧 UK BBC Documentary ($0.00)">
                <option value="kokoro:bm_george">George (UK BBC Documentary Male)</option>
                <option value="kokoro:bf_emma">Emma (UK Elegant Presenter Female)</option>
              </optgroup>
              <optgroup label="🇮🇳 Indian English & Hindi ($0.00)">
                <option value="en-IN-PrabhatNeural">Prabhat (Indian English Male — Natural)</option>
                <option value="en-IN-NeerjaExpressiveNeural">Neerja (Indian English Female — Expressive)</option>
                <option value="hi-IN-MadhurNeural">Madhur (Hindi Indian Male — Storyteller)</option>
                <option value="hi-IN-SwaraNeural">Swara (Hindi Indian Female — Conversational)</option>
              </optgroup>
              <optgroup label="🇳🇵 Authentic Nepali ($0.00)">
                <option value="ne-NP-SagarNeural">Sagar (Nepali Male — Authentic Himalayan)</option>
                <option value="ne-NP-HemkalaNeural">Hemkala (Nepali Female — Authentic Himalayan)</option>
              </optgroup>
              <optgroup label="🌐 Global Tech & Explainer ($0.00)">
                <option value="en-US-GuyNeural">Guy (US SaaS / Tech Explainer Male)</option>
                <option value="en-US-AriaNeural">Aria (US Dynamic Presenter Female)</option>
                <option value="en-GB-RyanNeural">Ryan (UK Fast Documentary Male)</option>
              </optgroup>
            </select>
            <div className="muted" style={{ fontSize: "0.72rem" }}>
              ⚡ Word-level karaoke captions synchronized via Kokoro phonemes &amp; Whisper speech boundaries.
            </div>
          </div>

          {/* Card D: Video Duration Matrix & Word Budget */}
          <div style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 10, padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <label style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                ⏱️ Target Duration &amp; Words:
              </label>
              <span className="badge ok" style={{ fontWeight: 700, fontSize: "0.7rem" }}>
                ~{Math.round(duration * (150 / 60))} Words @ 150 WPM
              </span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 6 }}>
              {[
                { s: 30, label: "30s Short" },
                { s: 60, label: "60s Viral" },
                { s: 120, label: "2 Min" },
                { s: 180, label: "3 Min" },
                { s: 300, label: "5 Min" },
                { s: 600, label: "10 Min Max" },
              ].map(d => (
                <button
                  key={d.s}
                  type="button"
                  className={`secondary ${duration === d.s ? "active" : ""}`}
                  onClick={() => setDuration(d.s)}
                  style={{
                    fontSize: "0.74rem",
                    padding: "8px 4px",
                    textAlign: "center",
                    border: duration === d.s ? "2px solid #ffd60a" : undefined,
                    color: duration === d.s ? "#ffd60a" : undefined,
                    fontWeight: duration === d.s ? 800 : 500
                  }}
                >
                  {d.label}
                </button>
              ))}
            </div>
            <div className="muted" style={{ fontSize: "0.72rem", marginTop: 8 }}>
              Pacing auto-calculated to maintain retention thresholds without filler words.
            </div>
          </div>
        </div>
      </section>

      {/* 3. Production Placeholders & Content Engine */}
      <section className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.1rem" }}>3. Production Placeholders &amp; Content Engine</h2>
            <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.82rem" }}>
              Choose Master Automated mode, URL &amp; Reference Media Ingestion, or Granular Manual mode.
            </p>
          </div>
          <div className="tab-bar" style={{ margin: 0, border: 0, padding: 0 }}>
            <button
              type="button"
              className={`tab-btn ${inputMode === "master" ? "active" : ""}`}
              onClick={() => setInputMode("master")}
            >
              ⚡ Master Automated Placeholder
            </button>
            <button
              type="button"
              className={`tab-btn ${inputMode === "url_reference" ? "active" : ""}`}
              onClick={() => setInputMode("url_reference")}
            >
              🔗 URL &amp; Media Reference Analyzer
            </button>
            <button
              type="button"
              className={`tab-btn ${inputMode === "manual" ? "active" : ""}`}
              onClick={() => setInputMode("manual")}
            >
              🎛️ Granular Multi-Placeholders
            </button>
          </div>
        </div>

        {/* Tab A: Master Automated Mode */}
        {inputMode === "master" && (
          <div>
            <label style={{ display: "block", fontWeight: 600, fontSize: "0.88rem", marginBottom: 6 }}>
              Master Concept, Topic, Article URL, or Raw Script:
            </label>
            <textarea
              rows={4}
              value={topic}
              onChange={e => setTopic(e.target.value)}
              placeholder="e.g. How to grow a YouTube channel from 0 to 100K subscribers using the 1-in-10 rule and thumbnail psychology..."
              style={{
                width: "100%",
                background: "var(--panel-alt)",
                border: "1px solid var(--line)",
                borderRadius: 8,
                padding: 12,
                color: "var(--ink)",
                fontFamily: "inherit",
                fontSize: "0.95rem",
                resize: "vertical"
              }}
            />
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 8 }}>
              <span className="muted" style={{ fontSize: "0.78rem" }}>
                💡 Tip: Paste any link, bullet list, podcast excerpt, or pitch deck. The AI deconstructs it into a viral storyboard.
              </span>
              <div style={{ display: "flex", gap: 10 }}>
                <button
                  type="button"
                  className="btn"
                  disabled={busyScript}
                  onClick={generateMasterScriptOnly}
                  style={{ background: "#ffd60a", color: "#000", fontWeight: 800 }}
                >
                  {busyScript ? "Generating Script..." : "📝 Step 1: Generate Master Script"}
                </button>
                <button
                  type="button"
                  className="btn"
                  disabled={busyAudio}
                  onClick={synthesizeVoiceAndLivePlayer}
                  style={{ background: "#38bdf8", color: "#000", fontWeight: 800 }}
                >
                  {busyAudio ? "Synthesizing Audio..." : "▶️ Step 2: Live Play Video"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Tab B: URL & Reference Media Analyzer with Avatar Transformation */}
        {inputMode === "url_reference" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div style={{
              background: "rgba(56, 189, 248, 0.08)",
              border: "1px solid rgba(56, 189, 248, 0.25)",
              borderRadius: 8,
              padding: "10px 14px",
              fontSize: "0.82rem"
            }}>
              <strong>🔗 Reference Media Deconstruction &amp; Avatar Transformation:</strong>
              <div className="muted" style={{ marginTop: 2 }}>
                Paste any YouTube video, Shorts, Reels, TikTok, Podcast clip, PDF, or Pitch Deck. The system analyzes narrative pacing, extracts punchlines, and transforms human presenters into stylized 2D/3D cartoon avatars.
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: 12 }}>
              <div>
                <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                  Reference Media URL (YouTube, Shorts, Reels, TikTok, PDF, Slide Deck):
                </label>
                <input
                  type="text"
                  value={referenceUrl}
                  onChange={e => setReferenceUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=... or https://instagram.com/reel/..."
                  style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                  Human Presenter → Cartoon Avatar Style:
                </label>
                <select
                  value={humanAvatarTransform}
                  onChange={e => setHumanAvatarTransform(e.target.value)}
                  style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)", color: "var(--text)" }}
                >
                  <option value="2d_cartoon">🎨 2D Flat Vector Cartoon (Kurzgesagt / Vox style)</option>
                  <option value="3d_pixar">✨ 3D Pixar / Disney Stylized Avatar</option>
                  <option value="sticky_doodle">✏️ Sticky Line-Art &amp; Doodle Character (MinutePhysics)</option>
                  <option value="vox_paper_cutout">📰 Vox Torn Paper Cutout Face with Moving Mouth</option>
                  <option value="cyberpunk_anime">⚡ Retro Anime / Cyberpunk Character</option>
                </select>
              </div>
            </div>

            <div>
              <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                Target Angle / Custom Topic Remix (Optional):
              </label>
              <input
                type="text"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                placeholder="e.g. Keep the same viral hook and pacing, but adapt it for SaaS tech founders"
                style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
              />
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 4 }}>
              <button
                type="button"
                className="btn"
                disabled={busyScript}
                onClick={generateMasterScriptOnly}
                style={{ background: "#ffd60a", color: "#000", fontWeight: 800 }}
              >
                {busyScript ? "Analyzing..." : "📝 Step 1: Generate Master Script"}
              </button>
              <button
                type="button"
                className="btn"
                disabled={busyAudio}
                onClick={synthesizeVoiceAndLivePlayer}
                style={{ background: "#38bdf8", color: "#000", fontWeight: 800 }}
              >
                {busyAudio ? "Synthesizing Audio..." : "▶️ Step 2: Live Play Video"}
              </button>
            </div>
          </div>
        )}

        {/* Tab C: Granular Multi-Placeholders */}
        {inputMode === "manual" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                1. Main Topic &amp; Core Thesis:
              </label>
              <input
                type="text"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                placeholder="e.g. The 30-Day Wall: Why 99% of creators quit"
                style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                  2. Hook &amp; High-Stakes Intrigue (Scene 1):
                </label>
                <input
                  type="text"
                  value={hookPlaceholder}
                  onChange={e => setHookPlaceholder(e.target.value)}
                  placeholder="e.g. Most people quit right before success"
                  style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
                />
              </div>
              <div>
                <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                  3. Underlying Problem &amp; Friction:
                </label>
                <input
                  type="text"
                  value={problemPlaceholder}
                  onChange={e => setProblemPlaceholder(e.target.value)}
                  placeholder="e.g. The Plateau of Latent Potential where effort yields 0 visible results"
                  style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
                />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                  4. Mechanism / Breakthrough:
                </label>
                <input
                  type="text"
                  value={mechanismPlaceholder}
                  onChange={e => setMechanismPlaceholder(e.target.value)}
                  placeholder="e.g. 32° Ice Cube Phase Change heating room with zero melt until threshold"
                  style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
                />
              </div>
              <div>
                <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                  5. Metric / Stat Lock (Proof):
                </label>
                <input
                  type="text"
                  value={metricPlaceholder}
                  onChange={e => setMetricPlaceholder(e.target.value)}
                  placeholder="e.g. 99% quit at day 29, outlast the silence"
                  style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
                />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              <div>
                <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                  6. B-Roll &amp; Layered Props:
                </label>
                <input
                  type="text"
                  value={brollSelection}
                  onChange={e => setBrollSelection(e.target.value)}
                  placeholder="e.g. 3D Calendar habit tracker, rubber stamp, red strike line"
                  style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
                />
              </div>
              <div>
                <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                  7. Brand Assets &amp; Golden CTA:
                </label>
                <input
                  type="text"
                  value={brandLogoUrl}
                  onChange={e => setBrandLogoUrl(e.target.value)}
                  placeholder="e.g. Logo PNG url, 'SUBSCRIBE TO THE MASTERCLASS' button"
                  style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
                />
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, marginTop: 8 }}>
              <button
                type="button"
                className="btn"
                disabled={busyScript}
                onClick={generateMasterScriptOnly}
                style={{ background: "#ffd60a", color: "#000", fontWeight: 800 }}
              >
                {busyScript ? "Generating..." : "📝 Step 1: Generate Master Script"}
              </button>
              <button
                type="button"
                className="btn"
                disabled={busyAudio}
                onClick={synthesizeVoiceAndLivePlayer}
                style={{ background: "#38bdf8", color: "#000", fontWeight: 800 }}
              >
                {busyAudio ? "Synthesizing Audio..." : "▶️ Step 2: Live Play Video"}
              </button>
            </div>
          </div>
        )}
      </section>

      {/* 4. Generated Blueprint Inspector, Theater Live Player & Token Telemetry */}
      {blueprint && (
        <section className="card" style={{
          background: "linear-gradient(180deg, var(--panel) 0%, rgba(12, 12, 18, 0.99) 100%)",
          border: "1px solid rgba(56, 189, 248, 0.4)",
          boxShadow: "0 25px 70px rgba(0,0,0,0.85)"
        }}>
          {/* Action Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 14, marginBottom: 16 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <span className="badge ok">✓ Master Blueprint Ready</span>
                <span className="badge">{blueprint.niche.badge}</span>
                <span className="badge">{blueprint.target_duration_s}s ({blueprint.scenes.length} Scenes)</span>
                <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", border: "1px solid #38bdf8" }}>
                  {blueprint.aspect_ratio} ({blueprint.aspect_ratio === "9:16" ? "Shorts Safe" : "Widescreen"})
                </span>
                <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a", border: "1px solid #ffd60a" }}>
                  🎙️ {blueprint.voice_id || selectedVoiceId}
                </span>
              </div>
              <h2 style={{ margin: "6px 0 0", fontSize: "1.35rem" }}>
                {blueprint.project_title}
              </h2>
            </div>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
              {/* Step 2 Trigger if not yet synthesized */}
              {!blueprint.has_audio && (
                <button
                  type="button"
                  className="btn"
                  disabled={busyAudio}
                  onClick={synthesizeVoiceAndLivePlayer}
                  style={{
                    background: "linear-gradient(135deg, #38bdf8 0%, #0284c7 100%)",
                    color: "#fff",
                    fontWeight: 800,
                    boxShadow: "0 4px 15px rgba(56, 189, 248, 0.4)"
                  }}
                >
                  {busyAudio ? "Synthesizing Audio..." : "▶️ Step 2: Synthesize Voice & Live Player"}
                </button>
              )}

              {/* Step 3: Local MP4 Render Button */}
              <button
                type="button"
                className="btn"
                disabled={renderingMp4 || !blueprint.html_file}
                onClick={renderFinalMp4}
                style={{
                  background: renderedMp4Result ? "#30d158" : "linear-gradient(135deg, #e11d48 0%, #be123c 100%)",
                  color: "#fff",
                  fontWeight: 800,
                  boxShadow: "0 4px 15px rgba(225, 29, 72, 0.4)"
                }}
              >
                {renderingMp4 ? "⏳ Rendering Local MP4..." : (renderedMp4Result ? "✓ MP4 Rendered!" : "🎬 Step 3: Render Local MP4 Video")}
              </button>

              {renderedMp4Result && (
                <a
                  href={renderedMp4Result.download_url}
                  download={renderedMp4Result.filename}
                  className="btn ok"
                  style={{ background: "#30d158", color: "#000", fontWeight: 800, textDecoration: "none" }}
                >
                  ⬇️ Download {renderedMp4Result.filename}
                </a>
              )}

              {blueprint.standalone_html_code && (
                <button
                  type="button"
                  className="btn"
                  onClick={downloadHtmlFile}
                  style={{ background: "#ffd60a", color: "#000", fontWeight: 700 }}
                >
                  💾 Download .html
                </button>
              )}

              <button
                type="button"
                className="btn"
                onClick={copyPromptToClipboard}
                style={{ background: copiedPrompt ? "#30d158" : "#38bdf8", color: "#000", fontWeight: 700 }}
              >
                {copiedPrompt ? "✓ Copied AI Prompt!" : "📋 Copy Prompt for AI"}
              </button>
              <button
                type="button"
                className="btn secondary"
                onClick={downloadPromptFile}
              >
                💾 Save .md Prompt
              </button>
            </div>
          </div>

          {/* Live Token & Cost Telemetry Widget */}
          {blueprint.token_telemetry && (
            <div style={{
              background: "rgba(10, 15, 28, 0.95)",
              border: "1px solid rgba(56, 189, 248, 0.3)",
              borderRadius: 10,
              padding: "12px 16px",
              marginBottom: 16,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              flexWrap: "wrap",
              gap: 12
            }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontWeight: 800, color: "#38bdf8", fontSize: "0.88rem" }}>
                    📊 AWS Bedrock Official Telemetry:
                  </span>
                  <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a" }}>
                    {blueprint.token_telemetry.model_name}
                  </span>
                </div>
                <div className="muted" style={{ fontSize: "0.74rem", marginTop: 2 }}>
                  Direct On-Demand token telemetry computed according to official AWS Bedrock pricing schedule.
                </div>
              </div>

              <div style={{ display: "flex", gap: 14, flexWrap: "wrap", alignItems: "center" }}>
                <div style={{ textAlign: "right" }}>
                  <div className="muted" style={{ fontSize: "0.7rem" }}>TOTAL TOKENS</div>
                  <div style={{ fontWeight: 800, fontSize: "0.95rem", color: "#fff" }}>
                    {blueprint.token_telemetry.total_tokens.toLocaleString()} tokens
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div className="muted" style={{ fontSize: "0.7rem" }}>PROMPT / COMPLETION</div>
                  <div style={{ fontWeight: 700, fontSize: "0.85rem", color: "#94a3b8" }}>
                    {blueprint.token_telemetry.input_tokens} in / {blueprint.token_telemetry.output_tokens} out
                  </div>
                </div>
                <div style={{ textAlign: "right", background: "rgba(48, 209, 88, 0.15)", padding: "4px 10px", borderRadius: 6, border: "1px solid #30d158" }}>
                  <div style={{ fontSize: "0.68rem", color: "#30d158", fontWeight: 700 }}>ESTIMATED COST</div>
                  <div style={{ fontWeight: 900, fontSize: "1.05rem", color: "#30d158" }}>
                    ${blueprint.token_telemetry.total_cost_usd.toFixed(4)} USD
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Inspector Tabs */}
          <div className="tab-bar" style={{ marginBottom: 16 }}>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "storyboard" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("storyboard")}
              style={{ fontWeight: 700, color: activeInspectorTab === "storyboard" ? "#ffd60a" : undefined }}
            >
              📝 Master Script &amp; Choreography ({blueprint.scenes.length})
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "player" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("player")}
              style={{ fontWeight: 700, color: activeInspectorTab === "player" ? "#38bdf8" : undefined }}
            >
              ▶️ Theater Live Preview Player {blueprint.has_audio ? "✓" : "(Requires Step 2)"}
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "prompt" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("prompt")}
            >
              🤖 Multimodal AI Master Prompt
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "html" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("html")}
            >
              🌐 Standalone HTML5 Code
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "audio" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("audio")}
            >
              🎵 Film Audio Bus Scoring
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "raw" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("raw")}
            >
              ⚙️ Raw Blueprint JSON
            </button>
          </div>

          {/* TAB 1: Master Script & Storyboard Breakdown */}
          {activeInspectorTab === "storyboard" && (
            <div>
              <div style={{
                background: "rgba(255, 214, 10, 0.08)",
                border: "1px solid rgba(255, 214, 10, 0.25)",
                borderRadius: 8,
                padding: "10px 14px",
                marginBottom: 14,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                flexWrap: "wrap",
                gap: 10
              }}>
                <div>
                  <strong>📝 Master Video Script Outline:</strong>
                  <div className="muted" style={{ fontSize: "0.78rem", marginTop: 2 }}>
                    Every scene is paced at 150 WPM with human inflections, camera dynamics, and B-roll cues. Click <strong>Step 2</strong> above to synthesize real audio &amp; live play.
                  </div>
                </div>
                {!blueprint.has_audio && (
                  <button
                    type="button"
                    className="btn"
                    disabled={busyAudio}
                    onClick={synthesizeVoiceAndLivePlayer}
                    style={{ background: "#38bdf8", color: "#000", fontWeight: 800, fontSize: "0.82rem", padding: "6px 14px" }}
                  >
                    {busyAudio ? "Synthesizing..." : "▶️ Proceed to Step 2 (Live Player)"}
                  </button>
                )}
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 14 }}>
                {blueprint.scenes.map((s, idx) => (
                  <div
                    key={s.scene_number}
                    style={{
                      background: "var(--panel-alt)",
                      border: "1px solid var(--line)",
                      borderRadius: 10,
                      padding: 16
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                      <span style={{ fontWeight: 800, fontSize: "0.95rem", color: "#ffd60a" }}>
                        {s.title}
                      </span>
                      <span className="badge" style={{ fontSize: "0.72rem" }}>
                        {s.start_s}s - {s.end_s}s ({s.duration_s}s)
                      </span>
                    </div>

                    {/* Spoken Narration Script */}
                    <div style={{
                      background: "rgba(0,0,0,0.4)",
                      borderLeft: "3px solid #ffd60a",
                      borderRadius: 4,
                      padding: "8px 12px",
                      marginBottom: 10,
                      fontStyle: "italic",
                      fontSize: "0.86rem",
                      color: "#f4f1ea",
                      lineHeight: 1.45
                    }}>
                      &ldquo;{s.spoken_narration || s.narration_guidance}&rdquo;
                    </div>

                    <div style={{ fontSize: "0.78rem", marginBottom: 6, color: "#94a3b8" }}>
                      🎯 Target: ~{s.target_word_count} spoken words @ 150 WPM
                    </div>

                    <div style={{ fontSize: "0.78rem", marginBottom: 5 }}>
                      <strong>Visual Motion:</strong> <code>{s.visual_choreography}</code>
                    </div>
                    <div style={{ fontSize: "0.78rem", marginBottom: 5 }}>
                      <strong>B-Roll Layer:</strong> {s.broll_layers}
                    </div>
                    <div style={{ fontSize: "0.78rem", marginBottom: 5 }}>
                      <strong>Camera Move:</strong> {s.camera_move}
                    </div>
                    <div style={{ fontSize: "0.78rem", color: "#30d158" }}>
                      <strong>SFX Cue:</strong> {s.sound_effects} · <strong>Cut:</strong> {s.transition_out}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: Theater Live Preview Player (Overhauled Luxury Device Mockup) */}
          {activeInspectorTab === "player" && (
            <div>
              {/* Not yet synthesized warning / call-to-action */}
              {!blueprint.has_audio ? (
                <div style={{
                  background: "rgba(56, 189, 248, 0.1)",
                  border: "1px solid #38bdf8",
                  borderRadius: 12,
                  padding: 24,
                  textAlign: "center"
                }}>
                  <h3 style={{ margin: "0 0 8px", color: "#38bdf8" }}>▶️ Live Player Requires Voice Synthesis (Step 2)</h3>
                  <p className="muted" style={{ margin: "0 0 16px", maxWidth: 600, marginLeft: "auto", marginRight: "auto" }}>
                    Your master script is ready! Click the button below to synthesize your chosen voiceover ({selectedVoiceId}), generate word-by-word karaoke timestamps, and compile your interactive player.
                  </p>
                  <button
                    type="button"
                    className="btn"
                    disabled={busyAudio}
                    onClick={synthesizeVoiceAndLivePlayer}
                    style={{ background: "#ffd60a", color: "#000", fontWeight: 800, padding: "10px 24px" }}
                  >
                    {busyAudio ? "Synthesizing Audio..." : "▶️ Synthesize Audio & Launch Theater Player"}
                  </button>
                </div>
              ) : (
                <div>
                  {/* Theater Control Strip */}
                  <div style={{
                    background: "rgba(14, 16, 26, 0.95)",
                    border: "1px solid rgba(255, 214, 10, 0.3)",
                    borderRadius: 10,
                    padding: "10px 16px",
                    marginBottom: 16,
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: 10
                  }}>
                    <div>
                      <strong>🎬 Theater Screening Room:</strong>
                      <div className="muted" style={{ fontSize: "0.76rem" }}>
                        Format: <strong>{aspect === "9:16" ? "9:16 Vertical Smartphone" : "16:9 Cinema Monitor"}</strong> · Synced Voice &amp; Word-by-Word Karaoke
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      <button
                        type="button"
                        className="btn"
                        disabled={renderingMp4}
                        onClick={renderFinalMp4}
                        style={{ background: "#e11d48", color: "#fff", fontWeight: 800, fontSize: "0.78rem", padding: "6px 14px" }}
                      >
                        {renderingMp4 ? "⏳ Rendering MP4..." : "🎬 Render Local MP4"}
                      </button>
                      <button
                        type="button"
                        className="btn"
                        onClick={downloadHtmlFile}
                        style={{ background: "#ffd60a", color: "#000", fontWeight: 700, fontSize: "0.78rem", padding: "6px 14px" }}
                      >
                        💾 Download .html
                      </button>
                    </div>
                  </div>

                  {/* Scene Navigation Jumper Chips */}
                  <div style={{
                    display: "flex",
                    gap: 6,
                    overflowX: "auto",
                    paddingBottom: 10,
                    marginBottom: 14
                  }}>
                    {blueprint.scenes.map((s, idx) => (
                      <button
                        key={s.scene_number}
                        type="button"
                        className={`secondary ${activeSceneIdx === idx ? "active" : ""}`}
                        onClick={() => jumpToScene(idx, s.start_s)}
                        style={{
                          fontSize: "0.72rem",
                          padding: "6px 12px",
                          borderRadius: 99,
                          whiteSpace: "nowrap",
                          border: activeSceneIdx === idx ? "1px solid #ffd60a" : undefined,
                          color: activeSceneIdx === idx ? "#ffd60a" : undefined,
                          fontWeight: activeSceneIdx === idx ? 800 : 500
                        }}
                      >
                        🎬 Scene {s.scene_number}: {s.title.split(': ')[1] || s.title} ({s.start_s}s)
                      </button>
                    ))}
                  </div>

                  {/* Luxury Theater Layout: Device Frame + Director Teleprompter */}
                  <div style={{
                    display: "grid",
                    gridTemplateColumns: aspect === "9:16" ? "minmax(360px, 460px) 1fr" : "1fr",
                    gap: 20,
                    alignItems: "start"
                  }}>
                    {/* Device Frame Mockup */}
                    <div style={{
                      margin: "0 auto",
                      width: "100%",
                      maxWidth: aspect === "9:16" ? "440px" : "1040px",
                      background: "#08080c",
                      padding: aspect === "9:16" ? "14px 10px" : "12px",
                      borderRadius: aspect === "9:16" ? 36 : 14,
                      border: aspect === "9:16" ? "4px solid #222230" : "2px solid #222230",
                      boxShadow: "0 30px 80px rgba(0,0,0,0.95)",
                      position: "relative"
                    }}>
                      {/* Smartphone Speaker Notch Mockup (9:16 only) */}
                      {aspect === "9:16" && (
                        <div style={{
                          width: 80,
                          height: 5,
                          background: "#222230",
                          borderRadius: 99,
                          margin: "0 auto 10px"
                        }} />
                      )}

                      <div style={{
                        borderRadius: aspect === "9:16" ? 22 : 8,
                        overflow: "hidden",
                        border: "1px solid rgba(255,255,255,0.06)",
                        background: "#000"
                      }}>
                        <iframe
                          ref={iframeRef}
                          title="Live Animation Stage"
                          srcDoc={liveHtmlSrcDoc || blueprint.standalone_html_code}
                          style={{
                            width: "100%",
                            height: aspect === "9:16" ? "760px" : "580px",
                            border: 0,
                            display: "block"
                          }}
                          allow="fullscreen"
                          allowFullScreen
                          sandbox="allow-scripts allow-same-origin"
                        />
                      </div>
                    </div>

                    {/* Director's Live Teleprompter (Shown for 9:16 mode) */}
                    {aspect === "9:16" && blueprint.scenes[activeSceneIdx] && (
                      <div style={{
                        background: "var(--panel-alt)",
                        border: "1px solid var(--line)",
                        borderRadius: 12,
                        padding: 18,
                        display: "flex",
                        flexDirection: "column",
                        gap: 12
                      }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a", fontWeight: 800 }}>
                            DIRECTOR TELEPROMPTER · SCENE {blueprint.scenes[activeSceneIdx].scene_number}
                          </span>
                          <span className="badge">
                            {blueprint.scenes[activeSceneIdx].start_s}s - {blueprint.scenes[activeSceneIdx].end_s}s
                          </span>
                        </div>

                        <div>
                          <label className="muted" style={{ fontSize: "0.72rem", textTransform: "uppercase" }}>Spoken Dialogue:</label>
                          <div style={{
                            background: "rgba(0,0,0,0.4)",
                            borderLeft: "3px solid #38bdf8",
                            padding: "10px 14px",
                            borderRadius: 6,
                            color: "#fff",
                            fontSize: "0.95rem",
                            lineHeight: 1.5,
                            marginTop: 4
                          }}>
                            &ldquo;{blueprint.scenes[activeSceneIdx].spoken_narration}&rdquo;
                          </div>
                        </div>

                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                          <div style={{ background: "rgba(0,0,0,0.3)", padding: 10, borderRadius: 6 }}>
                            <div className="muted" style={{ fontSize: "0.7rem" }}>CHOREOGRAPHY</div>
                            <div style={{ fontWeight: 700, fontSize: "0.82rem", color: "#ffd60a" }}>
                              {blueprint.scenes[activeSceneIdx].visual_choreography}
                            </div>
                          </div>
                          <div style={{ background: "rgba(0,0,0,0.3)", padding: 10, borderRadius: 6 }}>
                            <div className="muted" style={{ fontSize: "0.7rem" }}>CAMERA DYNAMICS</div>
                            <div style={{ fontWeight: 700, fontSize: "0.82rem", color: "#38bdf8" }}>
                              {blueprint.scenes[activeSceneIdx].camera_move}
                            </div>
                          </div>
                        </div>

                        <div style={{ background: "rgba(0,0,0,0.3)", padding: 10, borderRadius: 6 }}>
                          <div className="muted" style={{ fontSize: "0.7rem" }}>B-ROLL PROP LAYER</div>
                          <div style={{ fontWeight: 600, fontSize: "0.82rem", color: "#f4f1ea" }}>
                            {blueprint.scenes[activeSceneIdx].broll_layers}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: Multimodal AI Master Prompt */}
          {activeInspectorTab === "prompt" && (
            <div>
              <div style={{
                background: "rgba(56, 189, 248, 0.08)",
                border: "1px solid rgba(56, 189, 248, 0.25)",
                borderRadius: 8,
                padding: "10px 14px",
                marginBottom: 12,
                fontSize: "0.84rem",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}>
                <div>
                  <strong>How to use this in ChatGPT, Gemini, or Claude:</strong>
                  <ol style={{ margin: "4px 0 0", paddingLeft: 20 }}>
                    <li>Click the blue <strong>"Copy Prompt"</strong> button on the right.</li>
                    <li>Paste it into <strong>Google Gemini, ChatGPT, Claude, or DeepSeek</strong>.</li>
                    <li>Attach any reference file (PDF, PPT, Image, Video URL) if you have one.</li>
                    <li>The AI will write your complete script with the <strong>"What Next?"</strong> 1-click decision menu at the end!</li>
                  </ol>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    type="button"
                    className="btn"
                    onClick={copyPromptToClipboard}
                    style={{ background: copiedPrompt ? "#30d158" : "#38bdf8", color: "#000", fontWeight: 700, fontSize: "0.78rem", padding: "6px 12px" }}
                  >
                    {copiedPrompt ? "✓ Copied!" : "📋 Copy Prompt"}
                  </button>
                  <button
                    type="button"
                    className="btn secondary"
                    onClick={downloadPromptFile}
                    style={{ fontSize: "0.78rem", padding: "6px 12px" }}
                  >
                    💾 Save .md
                  </button>
                </div>
              </div>

              <pre style={{
                background: "#08080c",
                border: "1px solid var(--line)",
                borderRadius: 8,
                padding: 16,
                color: "#e2e8f0",
                fontSize: "0.82rem",
                lineHeight: 1.5,
                maxHeight: 520,
                overflowY: "auto",
                whiteSpace: "pre-wrap"
              }}>
                {blueprint.portable_master_prompt}
              </pre>
            </div>
          )}

          {/* TAB 4: Standalone HTML Code */}
          {activeInspectorTab === "html" && (
            <div>
              <div style={{
                background: "rgba(255, 214, 10, 0.08)",
                border: "1px solid rgba(255, 214, 10, 0.25)",
                borderRadius: 8,
                padding: "10px 14px",
                marginBottom: 12,
                fontSize: "0.84rem",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center"
              }}>
                <div>
                  <strong>⚡ Standalone HTML5 Video Animation Player Code:</strong>
                  <div className="muted" style={{ fontSize: "0.78rem", marginTop: 2 }}>
                    Self-contained single-file HTML document with interactive scrubber, canvas render loop, and responsive safe margin preview.
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    type="button"
                    className="btn"
                    onClick={copyHtmlToClipboard}
                    style={{ background: copiedHtml ? "#30d158" : "#ffd60a", color: "#000", fontWeight: 700, fontSize: "0.78rem", padding: "6px 12px" }}
                  >
                    {copiedHtml ? "✓ Copied!" : "📋 Copy HTML Code"}
                  </button>
                  <button
                    type="button"
                    className="btn secondary"
                    onClick={downloadHtmlFile}
                    style={{ fontSize: "0.78rem", padding: "6px 12px" }}
                  >
                    💾 Save .html
                  </button>
                </div>
              </div>

              <pre style={{
                background: "#08080c",
                border: "1px solid var(--line)",
                borderRadius: 8,
                padding: 16,
                color: "#ffd60a",
                fontSize: "0.8rem",
                lineHeight: 1.45,
                maxHeight: 520,
                overflowY: "auto",
                whiteSpace: "pre-wrap"
              }}>
                {blueprint.standalone_html_code || "Execute Step 2 to generate standalone HTML player code."}
              </pre>
            </div>
          )}

          {/* TAB 5: Film Audio Bus */}
          {activeInspectorTab === "audio" && (
            <div style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 8, padding: 18 }}>
              <h3 style={{ margin: "0 0 10px", fontSize: "1.1rem" }}>🎵 Film Audio Bus Scoring (100% Royalty-Free)</h3>
              <p className="muted" style={{ margin: "0 0 14px", fontSize: "0.84rem" }}>
                Zero copyright claim risk. Audio is synthetically mastered or procedurally composed with automated sidechain ducking.
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
                <div style={{ background: "rgba(0,0,0,0.3)", padding: 12, borderRadius: 6 }}>
                  <div className="muted" style={{ fontSize: "0.76rem" }}>MUSIC GENRE</div>
                  <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "#38bdf8" }}>{blueprint.music_bus.genre}</div>
                </div>
                <div style={{ background: "rgba(0,0,0,0.3)", padding: 12, borderRadius: 6 }}>
                  <div className="muted" style={{ fontSize: "0.76rem" }}>VOICE PROFILE</div>
                  <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "#ffd60a" }}>{blueprint.voice_id || selectedVoiceId}</div>
                </div>
                <div style={{ background: "rgba(0,0,0,0.3)", padding: 12, borderRadius: 6 }}>
                  <div className="muted" style={{ fontSize: "0.76rem" }}>SIDECHAIN DUCKING</div>
                  <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "#30d158" }}>{blueprint.music_bus.sidechain_ducking}</div>
                </div>
                <div style={{ background: "rgba(0,0,0,0.3)", padding: 12, borderRadius: 6 }}>
                  <div className="muted" style={{ fontSize: "0.76rem" }}>BROADCAST TARGET</div>
                  <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "#f43f5e" }}>{blueprint.music_bus.master_lufs} LUFS (Broadcast Standard)</div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: Raw JSON */}
          {activeInspectorTab === "raw" && (
            <pre style={{
              background: "#08080c",
              border: "1px solid var(--line)",
              borderRadius: 8,
              padding: 16,
              color: "#38bdf8",
              fontSize: "0.8rem",
              lineHeight: 1.45,
              maxHeight: 480,
              overflowY: "auto"
            }}>
              {JSON.stringify(blueprint, null, 2)}
            </pre>
          )}
        </section>
      )}

      {/* Workspace Plan & Generated Files Inspector */}
      {blueprint && (
        <section className="card" style={{ marginTop: 24, background: "rgba(12, 14, 22, 0.95)", border: "1px solid var(--line)" }}>
          <h3 style={{ margin: "0 0 10px", fontSize: "1.05rem" }}>📁 Workspace Assets &amp; File Manager</h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 12 }}>
            <div style={{ background: "var(--panel-alt)", padding: 12, borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontWeight: 700, fontSize: "0.85rem", color: "#38bdf8" }}>📄 Master Prompt File</div>
              <div className="muted" style={{ fontSize: "0.74rem", margin: "4px 0" }}>Portable prompt for Gemini, ChatGPT, Claude</div>
              <button type="button" className="secondary" onClick={downloadPromptFile} style={{ fontSize: "0.72rem", padding: "4px 8px", marginTop: 4 }}>
                💾 Download .md
              </button>
            </div>

            <div style={{ background: "var(--panel-alt)", padding: 12, borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontWeight: 700, fontSize: "0.85rem", color: "#ffd60a" }}>🌐 HTML5 Player Standalone</div>
              <div className="muted" style={{ fontSize: "0.74rem", margin: "4px 0" }}>Offline playable canvas animation bundle</div>
              <button type="button" className="secondary" disabled={!blueprint.standalone_html_code} onClick={downloadHtmlFile} style={{ fontSize: "0.72rem", padding: "4px 8px", marginTop: 4 }}>
                {blueprint.standalone_html_code ? "💾 Download .html" : "Pending Step 2"}
              </button>
            </div>

            <div style={{ background: "var(--panel-alt)", padding: 12, borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontWeight: 700, fontSize: "0.85rem", color: "#30d158" }}>🎬 Final Rendered MP4 Video</div>
              <div className="muted" style={{ fontSize: "0.74rem", margin: "4px 0" }}>Broadcast-grade 1080p video file</div>
              {renderedMp4Result ? (
                <a href={renderedMp4Result.download_url} download={renderedMp4Result.filename} className="btn ok" style={{ fontSize: "0.72rem", padding: "4px 8px", display: "inline-block", marginTop: 4 }}>
                  ⬇️ Download MP4
                </a>
              ) : (
                <button type="button" className="secondary" disabled={renderingMp4 || !blueprint.html_file} onClick={renderFinalMp4} style={{ fontSize: "0.72rem", padding: "4px 8px", marginTop: 4 }}>
                  {renderingMp4 ? "Rendering..." : "🎬 Execute Step 3 Render"}
                </button>
              )}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
