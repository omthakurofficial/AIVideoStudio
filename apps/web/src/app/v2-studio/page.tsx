"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  api,
  type V2NicheItem,
  type V2VoiceItem,
  type V2TemplateBlueprint,
  type V2SceneBlueprint,
} from "@/lib/api";

export default function V2StudioPage() {
  const [niches, setNiches] = useState<V2NicheItem[]>([]);
  const [voices, setVoices] = useState<V2VoiceItem[]>([]);
  const [selectedNicheId, setSelectedNicheId] = useState<string>("youtube_growth");
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>("kokoro:am_michael");
  const [inputMode, setInputMode] = useState<"master" | "manual">("master");

  // Master Mode Fields
  const [topic, setTopic] = useState("");
  const [duration, setDuration] = useState<number>(60);
  const [aspect, setAspect] = useState<"9:16" | "16:9">("9:16");

  // Manual Mode Granular Placeholders
  const [hookPlaceholder, setHookPlaceholder] = useState("");
  const [problemPlaceholder, setProblemPlaceholder] = useState("");
  const [mechanismPlaceholder, setMechanismPlaceholder] = useState("");
  const [metricPlaceholder, setMetricPlaceholder] = useState("");
  const [brollSelection, setBrollSelection] = useState("");
  const [brandLogoUrl, setBrandLogoUrl] = useState("");

  // Result & State
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [blueprint, setBlueprint] = useState<V2TemplateBlueprint | null>(null);
  const [activeInspectorTab, setActiveInspectorTab] = useState<"player" | "html" | "prompt" | "storyboard" | "audio" | "raw">("player");
  const [copiedPrompt, setCopiedPrompt] = useState(false);
  const [copiedHtml, setCopiedHtml] = useState(false);
  const [liveHtmlSrcDoc, setLiveHtmlSrcDoc] = useState<string>("");

  useEffect(() => {
    api.v2Niches().then(res => {
      setNiches(res.niches);
      if (res.voices) setVoices(res.voices);
      if (res.niches.length > 0) {
        setSelectedNicheId(res.niches[0].id);
        setTopic(res.niches[0].sample_topics[0]);
      }
    }).catch(err => {
      console.warn("Could not load v2 niches from backend API, using fallback", err);
    });
  }, []);

  const selectedNiche = niches.find(n => n.id === selectedNicheId) || niches[0];

  function handleSelectNiche(n: V2NicheItem, sampleTopic?: string) {
    setSelectedNicheId(n.id);
    setAspect(n.default_aspect);
    if (sampleTopic) {
      setTopic(sampleTopic);
    } else if (n.sample_topics?.length > 0) {
      setTopic(n.sample_topics[0]);
    }
  }

  async function generateBlueprint() {
    if (!topic.trim()) {
      setError("Please enter a topic or concept.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const customNotes = inputMode === "manual"
        ? `Manual Placeholders:
- Hook: ${hookPlaceholder}
- Problem: ${problemPlaceholder}
- Mechanism: ${mechanismPlaceholder}
- Metric: ${metricPlaceholder}
- B-Roll / Layered Props: ${brollSelection}
- Brand Assets: ${brandLogoUrl}`
        : undefined;

      const res = await api.v2GenerateTemplate({
        topic: topic.trim(),
        niche_id: selectedNicheId,
        target_duration_s: duration,
        aspect_ratio: aspect,
        mode: inputMode === "master" ? "master_auto" : "manual_placeholders",
        voice_id: selectedVoiceId,
        custom_instructions: customNotes,
      });
      setBlueprint(res);
      if (res.standalone_html_code) {
        setLiveHtmlSrcDoc(res.standalone_html_code);
        setActiveInspectorTab("player");
      }
    } catch (err) {
      setError((err as Error).message || "Template generation failed.");
    } finally {
      setBusy(false);
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
    <div style={{ maxWidth: 1300, margin: "0 auto", paddingBottom: 60 }}>
      {/* Studio Header */}
      <div className="card" style={{
        background: "linear-gradient(135deg, rgba(20, 20, 32, 0.95) 0%, rgba(10, 10, 16, 0.98) 100%)",
        border: "1px solid rgba(255, 214, 10, 0.25)",
        boxShadow: "0 10px 40px rgba(0,0,0,0.6)",
        marginBottom: 24
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
              <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a", border: "1px solid #ffd60a" }}>
                V2 PRODUCTION STUDIO
              </span>
              <span className="badge ok">10 Top Earning Niches</span>
              <span className="badge">Dual 16:9 &amp; 9:16 Engine</span>
              <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", border: "1px solid #38bdf8" }}>
                30s to 10 Min Max
              </span>
            </div>
            <h1 style={{ margin: "4px 0", fontSize: "1.75rem", fontFamily: "var(--font-display, inherit)", letterSpacing: "0.02em" }}>
              AI Video Studio V2 · Live Play &amp; Blueprint Engine
            </h1>
            <p className="muted" style={{ margin: 0, fontSize: "0.92rem", maxWidth: 900 }}>
              Generate viral templates with <strong>direct interactive HTML live play</strong>, natural neural TTS (Kokoro, Indian Male/Female, Nepali Male/Female, Whisper sync), and 1-click downloads for YouTube, Reels &amp; TikTok.
            </p>
          </div>
          <div style={{ display: "flex", gap: 10 }}>
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
              disabled={busy}
              onClick={generateBlueprint}
              style={{ background: "#ffd60a", color: "#000", fontWeight: 700 }}
            >
              {busy ? "Generating Blueprint..." : "✨ Generate & Live Play"}
            </button>
          </div>
        </div>
      </div>

      {error && <div role="alert" className="error" style={{ marginBottom: 20 }}>{error}</div>}

      {/* 1. Niche Archetypes Carousel / Grid */}
      <section className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.15rem" }}>1. Select Video Production Archetype (Top 10 YouTube &amp; Social Niches)</h2>
            <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.82rem" }}>
              Each niche loads custom kinetic typography, camera dynamics, color palettes, official icons, B-roll systems, and copyright-free audio scoring.
            </p>
          </div>
          {selectedNiche && (
            <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", border: "1px solid #38bdf8" }}>
              Active Archetype: {selectedNiche.name}
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
                    <span className="badge" style={{ fontSize: "0.7rem", padding: "2px 6px" }}>
                      {n.default_aspect}
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

      {/* 2. Format, Voice & Pacing Bar */}
      <section className="card" style={{ marginBottom: 24, background: "var(--panel)" }}>
        <h2 style={{ margin: "0 0 12px", fontSize: "1.1rem" }}>2. Audio Narration &amp; Duration Safe Margins (30s to 10 Min)</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
          {/* Aspect Ratio */}
          <div>
            <label style={{ display: "block", fontWeight: 600, fontSize: "0.85rem", marginBottom: 6 }}>
              Target Aspect Ratio &amp; Platform:
            </label>
            <div style={{ display: "flex", gap: 10 }}>
              <button
                type="button"
                className={`btn ${aspect === "9:16" ? "" : "secondary"}`}
                onClick={() => setAspect("9:16")}
                style={{ flex: 1, padding: "10px", textAlign: "center" }}
              >
                <div style={{ fontWeight: 700 }}>📱 9:16 Vertical</div>
                <div style={{ fontSize: "0.72rem", opacity: 0.8 }}>Shorts, Reels, TikTok (Safe Margins)</div>
              </button>
              <button
                type="button"
                className={`btn ${aspect === "16:9" ? "" : "secondary"}`}
                onClick={() => setAspect("16:9")}
                style={{ flex: 1, padding: "10px", textAlign: "center" }}
              >
                <div style={{ fontWeight: 700 }}>🖥️ 16:9 Landscape</div>
                <div style={{ fontSize: "0.72rem", opacity: 0.8 }}>YouTube &amp; Facebook Long-form</div>
              </button>
            </div>
          </div>

          {/* Voice Selector: Kokoro + Indian + Nepali + Global */}
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <label style={{ fontWeight: 600, fontSize: "0.85rem" }}>
                🎙️ Natural Neural Voice (Male / Female / Indian / Nepali):
              </label>
              <span className="badge ok" style={{ fontSize: "0.72rem" }}>
                $0.00 Free TTS
              </span>
            </div>
            <select
              value={selectedVoiceId}
              onChange={e => setSelectedVoiceId(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 8,
                border: "1px solid var(--line)",
                background: "var(--panel-alt)",
                color: "var(--text)",
                fontSize: "0.85rem"
              }}
            >
              <optgroup label="🇺🇸 & 🇬🇧 Local Kokoro Neural Voices ($0.00)">
                <option value="kokoro:am_michael">Michael (US Deep Documentary Male)</option>
                <option value="kokoro:af_heart">Heart (US Warm Expressive Female)</option>
                <option value="kokoro:af_bella">Bella (US Storyteller Female)</option>
                <option value="kokoro:am_adam">Adam (US Gritty Motivation Male)</option>
                <option value="kokoro:bm_george">George (UK BBC Documentary Male)</option>
                <option value="kokoro:bf_emma">Emma (UK Elegant Presenter Female)</option>
              </optgroup>
              <optgroup label="🇮🇳 Indian English & Hindi Neural Voices ($0.00)">
                <option value="en-IN-PrabhatNeural">Prabhat (Indian English Male — Natural)</option>
                <option value="en-IN-NeerjaExpressiveNeural">Neerja (Indian English Female — Expressive)</option>
                <option value="hi-IN-MadhurNeural">Madhur (Hindi Indian Male — Storyteller)</option>
                <option value="hi-IN-SwaraNeural">Swara (Hindi Indian Female — Conversational)</option>
              </optgroup>
              <optgroup label="🇳🇵 Nepali Authentic Neural Voices ($0.00)">
                <option value="ne-NP-SagarNeural">Sagar (Nepali Male — Authentic Himalayan)</option>
                <option value="ne-NP-HemkalaNeural">Hemkala (Nepali Female — Authentic Himalayan)</option>
              </optgroup>
              <optgroup label="🌐 Global Tech & Explainer Voices ($0.00)">
                <option value="en-US-GuyNeural">Guy (US Tech / SaaS Explainer Male)</option>
                <option value="en-US-AriaNeural">Aria (US Dynamic Presenter Female)</option>
                <option value="en-GB-RyanNeural">Ryan (UK Fast Documentary Male)</option>
              </optgroup>
            </select>
            <div className="muted" style={{ fontSize: "0.74rem", marginTop: 4 }}>
              ⚡ Word-level karaoke captions synchronized via Kokoro phonemes &amp; Whisper speech boundaries.
            </div>
          </div>

          {/* Duration Matrix (30s to 10 Minutes Max) */}
          <div style={{ gridColumn: "1 / -1" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <label style={{ fontWeight: 600, fontSize: "0.85rem" }}>
                Target Duration (30s to 10 Minutes Max):
              </label>
              <span className="badge ok" style={{ fontWeight: 700 }}>
                {duration >= 60 ? `${duration / 60} Min (${duration}s)` : `${duration}s`} · ~{Math.round(duration * (150 / 60))} Words @ 150 WPM
              </span>
            </div>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {[
                { s: 30, label: "30s Short" },
                { s: 60, label: "60s Viral" },
                { s: 120, label: "2 Min Explainer" },
                { s: 180, label: "3 Min Breakdown" },
                { s: 300, label: "5 Min Masterclass" },
                { s: 600, label: "10 Min Deep Documentary (Max)" },
              ].map(d => (
                <button
                  key={d.s}
                  type="button"
                  className={`secondary ${duration === d.s ? "active" : ""}`}
                  onClick={() => setDuration(d.s)}
                  style={{
                    flex: 1,
                    minWidth: 120,
                    fontSize: "0.78rem",
                    padding: "9px 6px",
                    textAlign: "center",
                    border: duration === d.s ? "2px solid #ffd60a" : undefined,
                    color: duration === d.s ? "#ffd60a" : undefined,
                    fontWeight: duration === d.s ? 700 : 500
                  }}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 3. Input Placeholders: Master Auto vs Granular Manual */}
      <section className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.1rem" }}>3. Production Placeholders &amp; Content Engine</h2>
            <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.82rem" }}>
              Choose between Master Automated mode (give topic/url, AI handles everything) or Granular Manual mode.
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
              className={`tab-btn ${inputMode === "manual" ? "active" : ""}`}
              onClick={() => setInputMode("manual")}
            >
              🎛️ Granular Multi-Placeholders
            </button>
          </div>
        </div>

        {inputMode === "master" ? (
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
              <button
                type="button"
                className="btn"
                disabled={busy}
                onClick={generateBlueprint}
                style={{ background: "#ffd60a", color: "#000", fontWeight: 700 }}
              >
                {busy ? "Synthesizing Template..." : "✨ Generate & Live Play"}
              </button>
            </div>
          </div>
        ) : (
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

            <div style={{ textAlign: "right", marginTop: 8 }}>
              <button
                type="button"
                className="btn"
                disabled={busy}
                onClick={generateBlueprint}
                style={{ background: "#ffd60a", color: "#000", fontWeight: 700 }}
              >
                {busy ? "Synthesizing Template..." : "✨ Generate & Live Play"}
              </button>
            </div>
          </div>
        )}
      </section>

      {/* 4. Generated Blueprint Inspector, Direct Live Player & Exporter */}
      {blueprint && (
        <section className="card" style={{
          background: "linear-gradient(180deg, var(--panel) 0%, rgba(12, 12, 18, 0.98) 100%)",
          border: "1px solid rgba(56, 189, 248, 0.35)",
          boxShadow: "0 20px 60px rgba(0,0,0,0.7)"
        }}>
          {/* Action Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 16 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <span className="badge ok">✓ Blueprint Ready</span>
                <span className="badge">{blueprint.niche.badge}</span>
                <span className="badge">{blueprint.target_duration_s}s ({blueprint.scenes.length} Scenes)</span>
                <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a", border: "1px solid #ffd60a" }}>
                  🎙️ {selectedVoiceId}
                </span>
              </div>
              <h2 style={{ margin: "4px 0 0", fontSize: "1.3rem" }}>
                {blueprint.project_title}
              </h2>
            </div>

            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button
                type="button"
                className="btn"
                onClick={downloadHtmlFile}
                style={{ background: "#ffd60a", color: "#000", fontWeight: 700 }}
              >
                💾 Download .html Player
              </button>
              <button
                type="button"
                className="btn"
                onClick={copyHtmlToClipboard}
                style={{ background: copiedHtml ? "#30d158" : "#22c55e", color: "#000", fontWeight: 700 }}
              >
                {copiedHtml ? "✓ Copied HTML Player!" : "🌐 Copy HTML Player Code"}
              </button>
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
                💾 Download .md Prompt
              </button>
            </div>
          </div>

          {/* Inspector Tabs */}
          <div className="tab-bar" style={{ marginBottom: 16 }}>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "player" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("player")}
              style={{ fontWeight: 700, color: activeInspectorTab === "player" ? "#ffd60a" : undefined }}
            >
              ▶️ Interactive Live Video Player
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
              className={`tab-btn ${activeInspectorTab === "prompt" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("prompt")}
            >
              🤖 Multimodal AI Master Prompt
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "storyboard" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("storyboard")}
            >
              🎬 Scene-by-Scene Choreography ({blueprint.scenes.length})
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "audio" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("audio")}
            >
              🎵 Copyright-Free Audio Bus
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "raw" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("raw")}
            >
              ⚙️ Raw Blueprint JSON
            </button>
          </div>

          {/* Tab 0: Direct Interactive Live Player in UI */}
          {activeInspectorTab === "player" && (
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
                  <strong>▶️ Direct In-Browser Live Video Player:</strong>
                  <div className="muted" style={{ fontSize: "0.78rem", marginTop: 2 }}>
                    Click <strong>Play</strong> below to preview the animation, timeline scrubber, kinetic headings, and sound right inside the Studio.
                  </div>
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    type="button"
                    className="btn"
                    onClick={downloadHtmlFile}
                    style={{ background: "#ffd60a", color: "#000", fontWeight: 700, fontSize: "0.78rem", padding: "6px 14px" }}
                  >
                    💾 Download .html Player
                  </button>
                </div>
              </div>

              {/* Responsive Iframe Stage Container */}
              <div style={{
                width: "100%",
                maxWidth: aspect === "9:16" ? "440px" : "1040px",
                margin: "0 auto",
                borderRadius: 14,
                overflow: "hidden",
                border: "2px solid rgba(255, 214, 10, 0.3)",
                boxShadow: "0 25px 60px rgba(0,0,0,0.85)",
                background: "#000"
              }}>
                <iframe
                  title="Live Animation Stage"
                  srcDoc={liveHtmlSrcDoc || blueprint.standalone_html_code}
                  style={{
                    width: "100%",
                    height: aspect === "9:16" ? "780px" : "585px",
                    border: 0,
                    display: "block"
                  }}
                  sandbox="allow-scripts allow-same-origin"
                />
              </div>
            </div>
          )}

          {/* Tab 1: Standalone HTML Code */}
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
                {blueprint.standalone_html_code || "Generating HTML Player..."}
              </pre>
            </div>
          )}

          {/* Tab 2: AI Prompt Box */}
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
                    <li>The AI will write your complete script, and automatically offer the <strong>"What Next?"</strong> 1-click decision menu at the end!</li>
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

          {/* Tab 3: Storyboard Breakdown */}
          {activeInspectorTab === "storyboard" && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 14 }}>
              {blueprint.scenes.map(s => (
                <div
                  key={s.scene_number}
                  style={{
                    background: "var(--panel-alt)",
                    border: "1px solid var(--line)",
                    borderRadius: 8,
                    padding: 14
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                    <span style={{ fontWeight: 700, fontSize: "0.92rem", color: "#ffd60a" }}>
                      {s.title}
                    </span>
                    <span className="badge" style={{ fontSize: "0.72rem" }}>
                      {s.start_s}s - {s.end_s}s ({s.duration_s}s)
                    </span>
                  </div>

                  <div style={{ fontSize: "0.8rem", marginBottom: 8, color: "#94a3b8" }}>
                    🎯 Target: ~{s.target_word_count} spoken words @ 150 WPM
                  </div>

                  <div style={{ fontSize: "0.8rem", marginBottom: 6 }}>
                    <strong>Visual Choreography:</strong> <code>{s.visual_choreography}</code>
                  </div>
                  <div style={{ fontSize: "0.8rem", marginBottom: 6 }}>
                    <strong>B-Roll Layer:</strong> {s.broll_layers}
                  </div>
                  <div style={{ fontSize: "0.8rem", marginBottom: 6 }}>
                    <strong>Camera Dynamics:</strong> {s.camera_move}
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "#30d158" }}>
                    <strong>SFX Cue:</strong> {s.sound_effects} · <strong>Cut:</strong> {s.transition_out}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tab 4: Audio Bus */}
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
                  <div style={{ fontWeight: 700, fontSize: "0.95rem", color: "#ffd60a" }}>{selectedVoiceId}</div>
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

          {/* Tab 5: Raw JSON */}
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
    </div>
  );
}
