"use client";

import Link from "next/link";
import { useEffect, useRef, useState, useMemo } from "react";
import {
  api,
  type V2NicheItem,
  type V2VoiceItem,
  type V2BedrockModelItem,
  type V2TokenTelemetry,
  type V2TemplateBlueprint,
  type V2SceneBlueprint,
} from "@/lib/api";

// 34 Verified AWS Bedrock Models Tested & Confirmed 200 OK on user account in ap-southeast-2
const VERIFIED_BEDROCK_MODELS: V2BedrockModelItem[] = [
  // 1. Anthropic Claude Suite (Claude 4.6 & 4.5 — Verified 200 OK)
  {
    id: "au.anthropic.claude-sonnet-4-6",
    name: "Claude Sonnet 4.6 (AU Profile — Latest Flagship)",
    vendor: "Anthropic",
    family: "Anthropic Claude",
    badge: "🧠 Flagship Reasoning ($3.00 / $15.00)",
    input_cost_per_1m: 3.00,
    output_cost_per_1m: 15.00,
    speed: "Balanced",
    is_best: true,
    status: "200_ok",
    description: "Latest Anthropic Claude 4.6 with state-of-the-art narrative pacing and viral retention choreography"
  },
  {
    id: "global.anthropic.claude-sonnet-4-6",
    name: "Claude Sonnet 4.6 (Global Profile)",
    vendor: "Anthropic",
    family: "Anthropic Claude",
    badge: "🧠 Flagship Global ($3.00 / $15.00)",
    input_cost_per_1m: 3.00,
    output_cost_per_1m: 15.00,
    speed: "Balanced",
    is_best: true,
    status: "200_ok",
    description: "Global cross-region Claude 4.6 profile for high-concurrency master blueprint generation"
  },
  {
    id: "au.anthropic.claude-opus-4-6-v1",
    name: "Claude Opus 4.6 (AU Profile — Maximum Reasoning)",
    vendor: "Anthropic",
    family: "Anthropic Claude",
    badge: "👑 Deepest Cinematic Analysis ($5.00 / $25.00)",
    input_cost_per_1m: 5.00,
    output_cost_per_1m: 25.00,
    speed: "Deliberate",
    is_best: true,
    status: "200_ok",
    description: "Maximum nuance and doctoral-level script density for long-form documentary and Vox explainers"
  },
  {
    id: "global.anthropic.claude-opus-4-6-v1",
    name: "Claude Opus 4.6 (Global Profile)",
    vendor: "Anthropic",
    family: "Anthropic Claude",
    badge: "👑 Global Opus Flagship ($5.00 / $25.00)",
    input_cost_per_1m: 5.00,
    output_cost_per_1m: 25.00,
    speed: "Deliberate",
    is_best: true,
    status: "200_ok",
    description: "Global cross-region Opus 4.6 with unmatched logical depth and character dialogue"
  },
  {
    id: "au.anthropic.claude-sonnet-4-5-20250929-v1:0",
    name: "Claude Sonnet 4.5 (AU Profile)",
    vendor: "Anthropic",
    family: "Anthropic Claude",
    badge: "🌟 Top Creator Choice ($3.00 / $15.00)",
    input_cost_per_1m: 3.00,
    output_cost_per_1m: 15.00,
    speed: "Balanced",
    is_best: true,
    status: "200_ok",
    description: "Established 4.5 creator flagship for high-converting hooks, timing, and pattern interrupts"
  },
  {
    id: "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    name: "Claude Sonnet 4.5 (Global Profile)",
    vendor: "Anthropic",
    family: "Anthropic Claude",
    badge: "🌟 Proven Sonnet 4.5 ($3.00 / $15.00)",
    input_cost_per_1m: 3.00,
    output_cost_per_1m: 15.00,
    speed: "Balanced",
    is_best: true,
    status: "200_ok",
    description: "Global cross-region 4.5 model with consistent narrative and script pacing"
  },
  {
    id: "au.anthropic.claude-haiku-4-5-20251001-v1:0",
    name: "Claude Haiku 4.5 (AU Profile — Fast)",
    vendor: "Anthropic",
    family: "Anthropic Claude",
    badge: "🚀 Fast & Low Cost ($1.00 / $5.00)",
    input_cost_per_1m: 1.00,
    output_cost_per_1m: 5.00,
    speed: "Very Fast",
    is_best: true,
    status: "200_ok",
    description: "Sub-second turnaround with high structured prompt precision for rapid script iteration"
  },
  {
    id: "global.anthropic.claude-haiku-4-5-20251001-v1:0",
    name: "Claude Haiku 4.5 (Global Profile)",
    vendor: "Anthropic",
    family: "Anthropic Claude",
    badge: "🚀 Global Fast Reasoning ($1.00 / $5.00)",
    input_cost_per_1m: 1.00,
    output_cost_per_1m: 5.00,
    speed: "Very Fast",
    is_best: false,
    status: "200_ok",
    description: "Fast global inference for bulk storyboard drafting"
  },
  {
    id: "global.anthropic.claude-opus-4-5-20251101-v1:0",
    name: "Claude Opus 4.5 (Global Profile — Flagship)",
    vendor: "Anthropic",
    family: "Anthropic Claude",
    badge: "👑 Opus 4.5 Flagship ($5.00 / $25.00)",
    input_cost_per_1m: 5.00,
    output_cost_per_1m: 25.00,
    speed: "Deliberate",
    is_best: false,
    status: "200_ok",
    description: "Deep narrative orchestration with complex multi-perspective framing"
  },

  // 2. Amazon Nova Suite (Verified 200 OK)
  {
    id: "apac.amazon.nova-pro-v1:0",
    name: "Amazon Nova Pro v1 (APAC)",
    vendor: "Amazon",
    family: "Amazon Nova",
    badge: "🌐 Multimodal Cinematic ($0.80 / $3.20)",
    input_cost_per_1m: 0.80,
    output_cost_per_1m: 3.20,
    speed: "Fast",
    is_best: true,
    status: "200_ok",
    description: "AWS native multimodal model tailored for complex scene choreography and visuals"
  },
  {
    id: "apac.amazon.nova-lite-v1:0",
    name: "Amazon Nova Lite v1 (APAC)",
    vendor: "Amazon",
    family: "Amazon Nova",
    badge: "💰 Ultra-Economical ($0.06 / $0.24)",
    input_cost_per_1m: 0.06,
    output_cost_per_1m: 0.24,
    speed: "Lightning",
    is_best: false,
    status: "200_ok",
    description: "Lowest cost Bedrock model available, saves 98% on token spend ($0.0002/video)"
  },
  {
    id: "global.amazon.nova-2-lite-v1:0",
    name: "Amazon Nova 2 Lite (Global)",
    vendor: "Amazon",
    family: "Amazon Nova",
    badge: "⚡ Next-Gen Nova 2 ($0.06 / $0.24)",
    input_cost_per_1m: 0.06,
    output_cost_per_1m: 0.24,
    speed: "Lightning",
    is_best: false,
    status: "200_ok",
    description: "Next-generation ultra-fast Nova architecture with improved instruction following"
  },
  {
    id: "apac.amazon.nova-micro-v1:0",
    name: "Amazon Nova Micro v1 (APAC)",
    vendor: "Amazon",
    family: "Amazon Nova",
    badge: "🪙 Micro Penny Cost ($0.035 / $0.14)",
    input_cost_per_1m: 0.035,
    output_cost_per_1m: 0.14,
    speed: "Lightning",
    is_best: false,
    status: "200_ok",
    description: "Near-zero cost per script (~$0.00008), ideal for bulk batch processing"
  },

  // 3. DeepSeek Suite (Verified 200 OK)
  {
    id: "deepseek.v3.2",
    name: "DeepSeek V3.2 (Bedrock On-Demand)",
    vendor: "DeepSeek",
    family: "DeepSeek",
    badge: "🎯 Viral Retention & Data Logic ($0.58 / $1.68)",
    input_cost_per_1m: 0.58,
    output_cost_per_1m: 1.68,
    speed: "Fast",
    is_best: true,
    status: "200_ok",
    description: "Specialized in pattern interrupts, contrarian angles, and analytical breakdowns"
  },
  {
    id: "deepseek.v3-v1:0",
    name: "DeepSeek V3.1 (Bedrock On-Demand)",
    vendor: "DeepSeek",
    family: "DeepSeek",
    badge: "🧠 Deep Analytical Story ($0.58 / $1.68)",
    input_cost_per_1m: 0.58,
    output_cost_per_1m: 1.68,
    speed: "Fast",
    is_best: false,
    status: "200_ok",
    description: "Precise factual deconstruction and structured scene sequencing"
  },

  // 4. Z.AI GLM Suite (Verified 200 OK)
  {
    id: "zai.glm-5",
    name: "Z.AI GLM 5 (1M Context Director)",
    vendor: "Z.AI (GLM)",
    family: "Z.AI (GLM)",
    badge: "🎯 1M Context Low Cost ($0.50 / $1.50)",
    input_cost_per_1m: 0.50,
    output_cost_per_1m: 1.50,
    speed: "Fast",
    is_best: true,
    status: "200_ok",
    description: "Exceptional narrative pacing with 1M token memory for long-form scripts"
  },
  {
    id: "zai.glm-4.7",
    name: "Z.AI GLM 4.7 (Balanced Director)",
    vendor: "Z.AI (GLM)",
    family: "Z.AI (GLM)",
    badge: "⚖️ Balanced Performance ($0.35 / $1.10)",
    input_cost_per_1m: 0.35,
    output_cost_per_1m: 1.10,
    speed: "Fast",
    is_best: false,
    status: "200_ok",
    description: "Cost-effective director with strong reasoning and dialogue tone synthesis"
  },
  {
    id: "zai.glm-4.7-flash",
    name: "Z.AI GLM 4.7 Flash (Ultra-Low Cost)",
    vendor: "Z.AI (GLM)",
    family: "Z.AI (GLM)",
    badge: "⚡ Ultra-Low Cost Flash ($0.07 / $0.25)",
    input_cost_per_1m: 0.07,
    output_cost_per_1m: 0.25,
    speed: "Lightning",
    is_best: false,
    status: "200_ok",
    description: "Sub-second turnaround and 95% cost saving for rapid concept testing"
  },

  // 5. NVIDIA Nemotron Suite (Verified 200 OK)
  {
    id: "nvidia.nemotron-super-3-120b",
    name: "NVIDIA Nemotron 3 Super 120B",
    vendor: "NVIDIA",
    family: "NVIDIA",
    badge: "🏎️ High-Reasoning Super ($0.40 / $1.20)",
    input_cost_per_1m: 0.40,
    output_cost_per_1m: 1.20,
    speed: "Fast",
    is_best: true,
    status: "200_ok",
    description: "NVIDIA enterprise flagship with rigorous mathematical and structured logic"
  },
  {
    id: "nvidia.nemotron-nano-3-30b",
    name: "NVIDIA Nemotron Nano 3 30B",
    vendor: "NVIDIA",
    family: "NVIDIA",
    badge: "🚀 Nano High-Speed ($0.12 / $0.36)",
    input_cost_per_1m: 0.12,
    output_cost_per_1m: 0.36,
    speed: "Ultra Fast",
    is_best: false,
    status: "200_ok",
    description: "Lightweight and ultra-responsive for instant scene storyboard generation"
  },
  {
    id: "nvidia.nemotron-nano-12b-v2",
    name: "NVIDIA Nemotron Nano 12B v2 (Ultra Fast)",
    vendor: "NVIDIA",
    family: "NVIDIA",
    badge: "⚡ Nano 12B v2 ($0.10 / $0.30)",
    input_cost_per_1m: 0.10,
    output_cost_per_1m: 0.30,
    speed: "Lightning",
    is_best: false,
    status: "200_ok",
    description: "Ultra-fast compact multimodal vision-language model for fast scene generation"
  },

  // 6. Moonshot AI Suite (Verified 200 OK)
  {
    id: "moonshotai.kimi-k2.5",
    name: "Moonshot AI Kimi K2.5 (Fast Director)",
    vendor: "Moonshot AI",
    family: "Moonshot AI",
    badge: "⚡ Fast Moonshot Director ($0.60 / $2.40)",
    input_cost_per_1m: 0.60,
    output_cost_per_1m: 2.40,
    speed: "Fast",
    is_best: true,
    status: "200_ok",
    description: "High-speed director for narrative pacing and natural character dialogue"
  },
  {
    id: "moonshot.kimi-k2-thinking",
    name: "Moonshot AI Kimi K2 Thinking",
    vendor: "Moonshot AI",
    family: "Moonshot AI",
    badge: "🤔 Deep Thought Process ($0.60 / $2.40)",
    input_cost_per_1m: 0.60,
    output_cost_per_1m: 2.40,
    speed: "Balanced",
    is_best: false,
    status: "200_ok",
    description: "Internal monologue reasoning for solving complex explanatory topics"
  },

  // 7. Qwen Suite (Verified 200 OK)
  {
    id: "qwen.qwen3-235b-a22b-2507-v1:0",
    name: "Qwen3 235B A22B (Bedrock On-Demand)",
    vendor: "Qwen",
    family: "Qwen",
    badge: "🌐 Multilingual Beast ($0.45 / $1.80)",
    input_cost_per_1m: 0.45,
    output_cost_per_1m: 1.80,
    speed: "Fast",
    is_best: true,
    status: "200_ok",
    description: "235B parameter multilingual power, incredible knowledge depth across global domains"
  },
  {
    id: "qwen.qwen3-32b-v1:0",
    name: "Qwen3 32B Dense (Bedrock On-Demand)",
    vendor: "Qwen",
    family: "Qwen",
    badge: "⚡ 32B Dense Speed ($0.15 / $0.60)",
    input_cost_per_1m: 0.15,
    output_cost_per_1m: 0.60,
    speed: "Ultra Fast",
    is_best: false,
    status: "200_ok",
    description: "Dense 32B model with exceptional speed and low cost for fast storytelling"
  },
  {
    id: "qwen.qwen3-coder-next",
    name: "Qwen3 Coder Next (Bedrock On-Demand)",
    vendor: "Qwen",
    family: "Qwen",
    badge: "💻 Tech Script & Logic ($0.40 / $1.60)",
    input_cost_per_1m: 0.40,
    output_cost_per_1m: 1.60,
    speed: "Fast",
    is_best: false,
    status: "200_ok",
    description: "Specialized in technical scriptwriting, developer tutorials, and code demonstrations"
  },

  // 8. MiniMax Suite (Verified 200 OK)
  {
    id: "minimax.minimax-m2.5",
    name: "MiniMax M2.5 (Bedrock On-Demand)",
    vendor: "MiniMax",
    family: "MiniMax",
    badge: "✍️ Conversational Narrative ($0.30 / $1.20)",
    input_cost_per_1m: 0.30,
    output_cost_per_1m: 1.20,
    speed: "Fast",
    is_best: true,
    status: "200_ok",
    description: "Natural human conversational cadence, ideal for podcasts and explainer dialogue"
  },
  {
    id: "minimax.minimax-m2.1",
    name: "MiniMax M2.1 (Bedrock On-Demand)",
    vendor: "MiniMax",
    family: "MiniMax",
    badge: "🎙️ Podcast Voice Tone ($0.25 / $1.00)",
    input_cost_per_1m: 0.25,
    output_cost_per_1m: 1.00,
    speed: "Fast",
    is_best: false,
    status: "200_ok",
    description: "Relaxed conversational pacing for narrative voiceovers"
  },

  // 9. Mistral AI Suite (Verified 200 OK)
  {
    id: "mistral.mistral-large-3-675b-instruct",
    name: "Mistral Large 3 675B Instruct",
    vendor: "Mistral AI",
    family: "Mistral AI",
    badge: "🌪️ 675B Flagship ($2.00 / $6.00)",
    input_cost_per_1m: 2.00,
    output_cost_per_1m: 6.00,
    speed: "Balanced",
    is_best: true,
    status: "200_ok",
    description: "European flagship 675B powerhouse with top-tier reasoning and code synthesis"
  },
  {
    id: "mistral.mistral-large-2402-v1:0",
    name: "Mistral Large 24.02 Instruct",
    vendor: "Mistral AI",
    family: "Mistral AI",
    badge: "⚡ Classic Large 24.02 ($2.00 / $6.00)",
    input_cost_per_1m: 2.00,
    output_cost_per_1m: 6.00,
    speed: "Balanced",
    is_best: false,
    status: "200_ok",
    description: "Stable, verified enterprise large reasoning model"
  },
  {
    id: "mistral.ministral-3-14b-instruct",
    name: "Ministral 14B 3.0",
    vendor: "Mistral AI",
    family: "Mistral AI",
    badge: "🚀 Lightweight 14B ($0.10 / $0.30)",
    input_cost_per_1m: 0.10,
    output_cost_per_1m: 0.30,
    speed: "Ultra Fast",
    is_best: false,
    status: "200_ok",
    description: "Fast, punchy dialogue synthesis at minimal token spend"
  },

  // 10. OpenAI on Bedrock (Verified 200 OK)
  {
    id: "openai.gpt-oss-120b-1:0",
    name: "OpenAI GPT OSS 120B (Bedrock)",
    vendor: "OpenAI",
    family: "OpenAI",
    badge: "🤖 OpenAI Flagship OSS ($0.50 / $1.50)",
    input_cost_per_1m: 0.50,
    output_cost_per_1m: 1.50,
    speed: "Fast",
    is_best: true,
    status: "200_ok",
    description: "OpenAI open weights model hosted natively on AWS Bedrock for advanced reasoning"
  },
  {
    id: "openai.gpt-oss-20b-1:0",
    name: "OpenAI GPT OSS 20B (Bedrock)",
    vendor: "OpenAI",
    family: "OpenAI",
    badge: "⚡ Fast OpenAI OSS ($0.15 / $0.60)",
    input_cost_per_1m: 0.15,
    output_cost_per_1m: 0.60,
    speed: "Ultra Fast",
    is_best: false,
    status: "200_ok",
    description: "Compact 20B OpenAI model for fast outlines and rapid iterations"
  },

  // 11. Google Gemma on Bedrock (Verified 200 OK)
  {
    id: "google.gemma-3-27b-it",
    name: "Google Gemma 3 27B IT (Bedrock)",
    vendor: "Google",
    family: "Google",
    badge: "🌐 Google Gemma 3 ($0.20 / $0.60)",
    input_cost_per_1m: 0.20,
    output_cost_per_1m: 0.60,
    speed: "Ultra Fast",
    is_best: false,
    status: "200_ok",
    description: "Google's open-weights 27B model deployed on AWS Bedrock for clean structured outputs"
  }
];

export default function V2StudioPage() {
  const [niches, setNiches] = useState<V2NicheItem[]>([]);
  const [voices, setVoices] = useState<V2VoiceItem[]>([]);
  const [models, setModels] = useState<V2BedrockModelItem[]>(VERIFIED_BEDROCK_MODELS);
  const [selectedNicheId, setSelectedNicheId] = useState<string>("youtube_growth");
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>("kokoro:am_michael");
  // Default to confirmed working Claude Sonnet 4.6 (HTTP 200 OK)
  const [selectedModelId, setSelectedModelId] = useState<string>("au.anthropic.claude-sonnet-4-6");
  const [inputMode, setInputMode] = useState<"master" | "url_reference" | "manual">("master");

  // Section 2.2 Filter & Sort States
  const [providerFilter, setProviderFilter] = useState<string>("all");
  const [sortFilter, setSortFilter] = useState<"best" | "cost_desc" | "cost_asc" | "fastest">("best");

  // Format, Duration & Concept Fields
  const [topic, setTopic] = useState("");
  const [duration, setDuration] = useState<number>(60);
  const [aspect, setAspect] = useState<"9:16" | "16:9">("9:16");

  // Mode 3B: URL Reference & Avatar Transform Fields
  const [referenceUrl, setReferenceUrl] = useState("");
  const [humanAvatarTransform, setHumanAvatarTransform] = useState("2d_cartoon");

  // Mode 3C: Granular Multi-Placeholders Fields
  const [hookPlaceholder, setHookPlaceholder] = useState("");
  const [problemPlaceholder, setProblemPlaceholder] = useState("");
  const [mechanismPlaceholder, setMechanismPlaceholder] = useState("");
  const [metricPlaceholder, setMetricPlaceholder] = useState("");
  const [brollSelection, setBrollSelection] = useState("");
  const [brandLogoUrl, setBrandLogoUrl] = useState("");
  const [manualReferenceUrl, setManualReferenceUrl] = useState(""); // Attached URL support in manual mode!

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

  // Dynamic Provider List with model counts
  const availableProviders = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const m of models) {
      const v = m.vendor || "Other";
      counts[v] = (counts[v] || 0) + 1;
    }
    return counts;
  }, [models]);

  // Filter & Sort Models according to User Selection
  const filteredAndSortedModels = useMemo(() => {
    let list = [...models];

    // 1. Filter by Provider
    if (providerFilter !== "all") {
      list = list.filter(m => (m.vendor || "").toLowerCase() === providerFilter.toLowerCase());
    }

    // 2. Sort Models
    if (sortFilter === "best") {
      list.sort((a, b) => {
        if (a.is_best && !b.is_best) return -1;
        if (!a.is_best && b.is_best) return 1;
        return b.output_cost_per_1m - a.output_cost_per_1m;
      });
    } else if (sortFilter === "cost_desc") {
      list.sort((a, b) => b.output_cost_per_1m - a.output_cost_per_1m);
    } else if (sortFilter === "cost_asc") {
      list.sort((a, b) => a.input_cost_per_1m - b.input_cost_per_1m);
    } else if (sortFilter === "fastest") {
      const speedRanks: Record<string, number> = {
        Lightning: 1,
        "Ultra Fast": 2,
        "Very Fast": 3,
        Fast: 4,
        Balanced: 5,
        Deliberate: 6
      };
      list.sort((a, b) => (speedRanks[a.speed] || 5) - (speedRanks[b.speed] || 5));
    }

    return list;
  }, [models, providerFilter, sortFilter]);

  const selectedModel = models.find(m => m.id === selectedModelId) || filteredAndSortedModels[0] || models[0];

  function handleSelectNiche(n: V2NicheItem, sampleTopic?: string) {
    setSelectedNicheId(n.id);
    setAspect(n.default_aspect);
    if (sampleTopic) {
      setTopic(sampleTopic);
    } else if (n.sample_topics?.length > 0) {
      setTopic(n.sample_topics[0]);
    }
  }

  function handleResetStudio() {
    setBlueprint(null);
    setRenderedMp4Result(null);
    setLiveHtmlSrcDoc("");
    setError(null);
  }

  function buildCustomInstructions(): string | undefined {
    if (inputMode === "url_reference") {
      return `Reference Analysis & Avatar Transformation:
- Source URL: ${referenceUrl.trim()}
- Presenter Avatar Style: ${humanAvatarTransform}
- Directive: Deconstruct reference video frame-by-frame: extract hook, retention drops, core punchlines. Re-synthesize narrative into chosen archetype (${selectedNiche?.name}), replace human presenter with animated ${humanAvatarTransform} avatar.`;
    }
    if (inputMode === "manual") {
      return `Granular Multi-Placeholders:
- Hook (Scene 1): ${hookPlaceholder}
- Problem / Friction: ${problemPlaceholder}
- Mechanism / Breakthrough: ${mechanismPlaceholder}
- Metric / Stat Lock: ${metricPlaceholder}
- B-Roll & Layered Props: ${brollSelection}
- Brand Assets & Golden CTA: ${brandLogoUrl}
- Attached Reference Media URL: ${manualReferenceUrl.trim() || "None"}`;
    }
    return undefined;
  }

  // ACTION 4.1: Generate Master Script & Blueprint (Instant & Zero Audio Wait)
  async function generateMasterScriptOnly() {
    let finalTopic = topic.trim();
    if (inputMode === "url_reference") {
      if (!referenceUrl.trim()) {
        setError("Please enter a reference URL (YouTube, Shorts, Reels, TikTok, PDF, or Deck link).");
        return;
      }
      finalTopic = topic.trim() || `Deconstructed Re-creation from: ${referenceUrl.trim()}`;
    } else {
      if (!finalTopic) {
        setError("Please enter a topic or concept.");
        return;
      }
    }

    const customNotes = buildCustomInstructions();
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

  // ACTION 4.2: Synthesize Voice Audio & Build Live Canvas Player (Step 2)
  async function synthesizeVoiceAndLivePlayer() {
    let finalTopic = topic.trim();
    if (inputMode === "url_reference") {
      if (!referenceUrl.trim()) {
        setError("Please enter a reference URL.");
        return;
      }
      finalTopic = topic.trim() || `Deconstructed Re-creation from: ${referenceUrl.trim()}`;
    } else {
      if (!finalTopic) {
        setError("Please enter or generate a master topic first.");
        return;
      }
    }

    const customNotes = buildCustomInstructions();
    setBusyAudio(true);
    setError(null);
    setRenderedMp4Result(null);
    try {
      const res = await api.v2SynthesizePlayer({
        topic: finalTopic,
        niche_id: selectedNicheId,
        target_duration_s: duration,
        aspect_ratio: aspect,
        mode: inputMode === "master" ? "master_auto" : (inputMode === "url_reference" ? "url_reference_remix" : "manual_placeholders"),
        voice_id: selectedVoiceId,
        model_id: selectedModelId,
        custom_instructions: customNotes,
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

  // ACTION 7.1: Render Final Local MP4 Video
  async function renderFinalMp4() {
    if (!blueprint?.html_file || !blueprint?.master_wav) {
      setError("Please synthesize the live player (Action 4.2) before rendering MP4.");
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

  // Pre-calculated live token estimate for selected model & duration
  const estWords = Math.round(duration * (150 / 60));
  const estInTokens = 420 + Math.round((topic || "").split(" ").length * 4) + (inputMode === "url_reference" ? 240 : 60);
  const estOutTokens = 360 + estWords * 3;
  const estTotalTokens = estInTokens + estOutTokens;
  const estCostUsd = selectedModel
    ? (estInTokens / 1_000_000) * selectedModel.input_cost_per_1m + (estOutTokens / 1_000_000) * selectedModel.output_cost_per_1m
    : 0.003;

  return (
    <div style={{ maxWidth: 1340, margin: "0 auto", paddingBottom: 60 }}>
      {/* Studio Header (Clean & Uncluttered: Duplicate Buttons Removed) */}
      <div className="card" style={{
        background: "linear-gradient(135deg, rgba(20, 20, 32, 0.98) 0%, rgba(10, 10, 16, 0.99) 100%)",
        border: "1px solid rgba(255, 214, 10, 0.3)",
        boxShadow: "0 10px 40px rgba(0,0,0,0.6)",
        marginBottom: 20
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4, flexWrap: "wrap" }}>
              <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a", border: "1px solid #ffd60a" }}>
                V2 PRODUCTION STUDIO
              </span>
              <span className="badge ok">10 Top Earning Niches</span>
              <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8", border: "1px solid #38bdf8" }}>
                {models.length} Bedrock Models (200 OK)
              </span>
              <span className="badge" style={{ background: "rgba(48, 209, 88, 0.15)", color: "#30d158", border: "1px solid #30d158" }}>
                Zero Token Waste
              </span>
              <span className="badge" style={{ background: "rgba(168, 85, 247, 0.15)", color: "#c084fc", border: "1px solid #c084fc" }}>
                100% Royalty-Free Audio
              </span>
            </div>
            <h1 style={{ margin: "4px 0", fontSize: "1.75rem", fontFamily: "var(--font-display, inherit)", letterSpacing: "0.02em" }}>
              AI Video Studio V2 · Live Play &amp; Master Blueprint Engine
            </h1>
            <p className="muted" style={{ margin: 0, fontSize: "0.88rem", maxWidth: 980 }}>
              Sequential 7-step pipeline: <strong>Step 1</strong> Archetypes → <strong>Step 2</strong> Format &amp; Bedrock Specs → <strong>Step 3</strong> Content Ingestion → <strong>Step 4</strong> Action Deck → <strong>Step 5</strong> Master Blueprint &amp; Token Telemetry → <strong>Step 6</strong> Theater Screening Room → <strong>Step 7</strong> MP4 Render Hub.
            </p>
          </div>

          {blueprint && (
            <button
              type="button"
              className="btn secondary"
              onClick={handleResetStudio}
              style={{ fontSize: "0.82rem", padding: "8px 14px", border: "1px solid rgba(255,255,255,0.15)" }}
              title="Clear current blueprint and start a fresh video"
            >
              🔄 Reset / New Video
            </button>
          )}
        </div>
      </div>

      {error && <div role="alert" className="error" style={{ marginBottom: 20 }}>{error}</div>}

      {/* Production Pipeline Breadcrumbs */}
      <div className="card" style={{
        background: "rgba(14, 16, 26, 0.95)",
        border: "1px solid rgba(255,255,255,0.08)",
        padding: "12px 18px",
        marginBottom: 24
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
          <strong style={{ fontSize: "0.86rem", color: "#e2e8f0" }}>🎯 Sequential Production Pipeline:</strong>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", fontSize: "0.78rem" }}>
            <span className="badge ok">Step 1: {selectedNiche?.badge}</span>
            <span className="badge" style={{ background: "rgba(56, 189, 248, 0.15)", color: "#38bdf8" }}>
              Step 2: {aspect} ({aspect === "9:16" ? "Shorts Safe" : "16:9 Cinema"})
            </span>
            <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a" }}>
              Bedrock: {selectedModel?.name?.split(" (")[0] || selectedModel?.name}
            </span>
            <span className="badge">
              Step 3: {inputMode === "master" ? "Mode 3A Auto" : (inputMode === "url_reference" ? "Mode 3B URL Remix" : "Mode 3C Granular")}
            </span>
            <span className={`badge ${blueprint ? "ok" : ""}`}>
              {blueprint ? "✓ Step 5 Script Ready" : "Step 4 Pending"}
            </span>
            <span className={`badge ${blueprint?.has_audio ? "ok" : ""}`}>
              {blueprint?.has_audio ? "✓ Step 6 Theater Ready" : "Live Player Pending"}
            </span>
            <span className={`badge ${renderedMp4Result ? "ok" : ""}`}>
              {renderedMp4Result ? "✓ Step 7 MP4 Rendered" : "MP4 Ready"}
            </span>
          </div>
        </div>
      </div>

      {/* STEP 1: Select Video Production Archetype (Top 10 Niches) */}
      <section className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.18rem" }}>Step 1: Select Video Production Archetype (Top 10 Niches)</h2>
            <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.82rem" }}>
              Each archetype loads tailored visual typography, camera dynamics, color palettes, official icons, and copyright-free scoring. Every niche supports <strong>both 16:9 Landscape &amp; 9:16 Shorts</strong>.
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
          {niches.map((n, idx) => {
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
                      1.{idx + 1} {n.badge}
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

      {/* STEP 2: Platform Format & AWS Bedrock AI Engine (With Provider Filter & Sort Controls) */}
      <section className="card" style={{ marginBottom: 24, background: "linear-gradient(180deg, var(--panel) 0%, rgba(14, 16, 26, 0.98) 100%)" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, flexWrap: "wrap", gap: 10 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.18rem" }}>Step 2: Platform Format &amp; AWS Bedrock AI Engine</h2>
            <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.82rem" }}>
              Filter by provider, sort by Best of Best or Cost (high-to-low / low-to-high), and lock your aspect ratio and voiceover pacing.
            </p>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span className="badge ok" style={{ fontSize: "0.75rem" }}>
              🟢 All {models.length} Models Verified 200 OK
            </span>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(310px, 1fr))", gap: 16 }}>
          {/* Sub-step 2.1: Aspect Ratio Strategy */}
          <div style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 10, padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <label style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                2.1 Aspect Ratio &amp; Safe Zones:
              </label>
              <span className="badge" style={{ fontSize: "0.68rem" }}>Single-Ratio Lock</span>
            </div>
            <p className="muted" style={{ fontSize: "0.74rem", margin: "0 0 10px" }}>
              Choose your platform target. Prompt tokens are strictly spent on <strong>one chosen ratio</strong> to prevent Bedrock token waste!
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

          {/* Sub-step 2.2: AWS Bedrock Model Selection (Provider Filter + Best of Best + Cost Sort) */}
          <div style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 10, padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8, flexWrap: "wrap", gap: 6 }}>
              <label style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                2.2 AWS Bedrock AI Engine:
              </label>
              <span className="badge ok" style={{ fontSize: "0.68rem" }}>
                {filteredAndSortedModels.length} Models Shown
              </span>
            </div>

            {/* Filter & Sort Controls Bar */}
            <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1.3fr", gap: 8, marginBottom: 10 }}>
              <div>
                <label className="muted" style={{ fontSize: "0.71rem", display: "block", marginBottom: 3 }}>
                  SELECT PROVIDER:
                </label>
                <select
                  value={providerFilter}
                  onChange={e => setProviderFilter(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "6px 8px",
                    borderRadius: 6,
                    border: "1px solid var(--line)",
                    background: "var(--panel)",
                    color: "var(--text)",
                    fontSize: "0.78rem"
                  }}
                >
                  <option value="all">🌐 All Providers ({models.length})</option>
                  {Object.entries(availableProviders).map(([prov, cnt]) => (
                    <option key={prov} value={prov}>
                      {prov} ({cnt} models)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="muted" style={{ fontSize: "0.71rem", display: "block", marginBottom: 3 }}>
                  SORT STRATEGY:
                </label>
                <select
                  value={sortFilter}
                  onChange={e => setSortFilter(e.target.value as "best" | "cost_desc" | "cost_asc" | "fastest")}
                  style={{
                    width: "100%",
                    padding: "6px 8px",
                    borderRadius: 6,
                    border: "1px solid var(--line)",
                    background: "var(--panel)",
                    color: "var(--text)",
                    fontSize: "0.78rem"
                  }}
                >
                  <option value="best">⭐ Best of Best (Flagships First)</option>
                  <option value="cost_desc">💎 Cost: High to Low (Premium)</option>
                  <option value="cost_asc">💲 Cost: Low to High (Budget)</option>
                  <option value="fastest">⚡ Speed: Ultra-Fast First</option>
                </select>
              </div>
            </div>

            {/* Model Selection Dropdown */}
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
                fontSize: "0.82rem",
                marginBottom: 8
              }}
            >
              {filteredAndSortedModels.map(m => (
                <option key={m.id} value={m.id}>
                  {m.is_best ? "⭐ " : ""}{m.name} — ${m.input_cost_per_1m.toFixed(2)} in / ${m.output_cost_per_1m.toFixed(2)} out per 1M
                </option>
              ))}
            </select>

            {/* Selected Model Preview Card with Live Pre-Calculation */}
            <div style={{
              background: "rgba(0,0,0,0.45)",
              border: "1px solid rgba(56, 189, 248, 0.25)",
              borderRadius: 8,
              padding: "8px 10px",
              fontSize: "0.73rem",
              lineHeight: 1.4
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", color: "#38bdf8", fontWeight: 700 }}>
                <span>{selectedModel?.is_best ? "⭐ Best Flagship: " : ""}{selectedModel?.name}</span>
                <span style={{ color: "#ffd60a" }}>Speed: {selectedModel?.speed}</span>
              </div>
              <div className="muted" style={{ marginTop: 2, fontSize: "0.71rem" }}>{selectedModel?.description}</div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid rgba(255,255,255,0.08)", marginTop: 6, paddingTop: 5 }}>
                <span className="muted">Est. Cost for {duration}s (~{estWords} words):</span>
                <span style={{ fontWeight: 800, color: "#30d158" }}>
                  ~{estTotalTokens.toLocaleString()} tok · ~${estCostUsd.toFixed(4)} USD
                </span>
              </div>
            </div>
          </div>

          {/* Sub-step 2.3: Neural Voiceover Accent & Free TTS Profile */}
          <div style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 10, padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <label style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                2.3 Voiceover Accent &amp; Gender:
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

          {/* Sub-step 2.4: Video Duration Matrix & Word Budget */}
          <div style={{ background: "var(--panel-alt)", border: "1px solid var(--line)", borderRadius: 10, padding: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <label style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                2.4 Target Duration &amp; Words:
              </label>
              <span className="badge ok" style={{ fontWeight: 700, fontSize: "0.7rem" }}>
                ~{estWords} Words @ 150 WPM
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

      {/* STEP 3: Content Ingestion & Mode Selection */}
      <section className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, flexWrap: "wrap", gap: 10 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.18rem" }}>Step 3: Content Ingestion &amp; Mode Selection</h2>
            <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.82rem" }}>
              Choose Master Automated mode, URL Reference Media Analyzer, or Granular Multi-Placeholders.
            </p>
          </div>
          <div className="tab-bar" style={{ margin: 0, border: 0, padding: 0 }}>
            <button
              type="button"
              className={`tab-btn ${inputMode === "master" ? "active" : ""}`}
              onClick={() => setInputMode("master")}
            >
              ⚡ Mode 3A: Master Automated Concept
            </button>
            <button
              type="button"
              className={`tab-btn ${inputMode === "url_reference" ? "active" : ""}`}
              onClick={() => setInputMode("url_reference")}
            >
              🔗 Mode 3B: URL &amp; Media Reference Analyzer
            </button>
            <button
              type="button"
              className={`tab-btn ${inputMode === "manual" ? "active" : ""}`}
              onClick={() => setInputMode("manual")}
            >
              🎛️ Mode 3C: Granular Multi-Placeholders
            </button>
          </div>
        </div>

        {/* Mode 3A: Master Automated Concept */}
        {inputMode === "master" && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6, flexWrap: "wrap", gap: 8 }}>
              <label style={{ fontWeight: 700, fontSize: "0.88rem" }}>
                3A.1 Master Concept, Topic, Article URL, or Raw Script:
              </label>
              {/* Relocated and clearly labeled Random Niche Topic button */}
              <button
                type="button"
                className="btn secondary"
                onClick={() => {
                  if (selectedNiche?.sample_topics?.length > 0) {
                    const randomTopic = selectedNiche.sample_topics[Math.floor(Math.random() * selectedNiche.sample_topics.length)];
                    setTopic(randomTopic);
                  }
                }}
                style={{ fontSize: "0.75rem", padding: "4px 10px", display: "flex", alignItems: "center", gap: 6 }}
                title={`Loads a high-retention viral scenario written specifically for ${selectedNiche?.name}`}
              >
                🎲 Load Sample Scenario for {selectedNiche?.badge || selectedNiche?.name}
              </button>
            </div>
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
            <div className="muted" style={{ fontSize: "0.76rem", marginTop: 6 }}>
              💡 Tip: Paste any link, bullet list, podcast excerpt, or pitch deck. The AI deconstructs it into a viral storyboard.
            </div>
          </div>
        )}

        {/* Mode 3B: URL & Reference Media Analyzer with Avatar Transformation */}
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
                  3B.1 Reference Media URL (YouTube, Shorts, Reels, TikTok, PDF, Slide Deck):
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
                  3B.2 Human Presenter → Cartoon Avatar Style:
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
                3B.3 Target Angle / Custom Topic Remix (Optional):
              </label>
              <input
                type="text"
                value={topic}
                onChange={e => setTopic(e.target.value)}
                placeholder="e.g. Keep the same viral hook and pacing, but adapt it for SaaS tech founders"
                style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
              />
            </div>
          </div>
        )}

        {/* Mode 3C: Granular Multi-Placeholders (All 8 Numbered Inputs with Reference Media URL) */}
        {inputMode === "manual" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                3C.1 Main Topic &amp; Core Thesis:
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
                  3C.2 Hook &amp; High-Stakes Intrigue (Scene 1):
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
                  3C.3 Underlying Problem &amp; Friction:
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
                  3C.4 Mechanism / Breakthrough:
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
                  3C.5 Metric / Stat Lock (Proof):
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
                  3C.6 B-Roll &amp; Layered Props:
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
                  3C.7 Brand Assets &amp; Golden CTA:
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

            {/* Added 3C.8: Reference Media URL in Manual Mode */}
            <div>
              <label style={{ display: "block", fontWeight: 600, fontSize: "0.84rem", marginBottom: 4 }}>
                3C.8 Attached Reference Media URL &amp; External Link (Optional):
              </label>
              <input
                type="text"
                value={manualReferenceUrl}
                onChange={e => setManualReferenceUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=... or Shorts, Reels, TikTok, PDF, Slide Deck, or article link"
                style={{ width: "100%", padding: 10, borderRadius: 6, border: "1px solid var(--line)", background: "var(--panel-alt)" }}
              />
              <div className="muted" style={{ fontSize: "0.72rem", marginTop: 4 }}>
                Attach any external video or document link so the AI factors in its pacing and facts along with your manual placeholders.
              </div>
            </div>
          </div>
        )}
      </section>

      {/* STEP 4: Execute Action Deck */}
      <section className="card" style={{
        marginBottom: 24,
        background: "linear-gradient(135deg, rgba(20, 20, 32, 0.95) 0%, rgba(12, 14, 22, 0.98) 100%)",
        border: "1px solid rgba(255, 214, 10, 0.3)",
        padding: "18px 22px"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 14 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.18rem" }}>Step 4: Execute Action Deck</h2>
            <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.84rem" }}>
              Choose <strong>Action 4.1</strong> to instantly generate the master script, prompts, and token telemetry, or <strong>Action 4.2</strong> to synthesize voice audio and launch the live interactive player.
            </p>
          </div>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
            <button
              type="button"
              className="btn"
              disabled={busyScript}
              onClick={generateMasterScriptOnly}
              style={{
                background: "#ffd60a",
                color: "#000",
                fontWeight: 800,
                padding: "12px 20px",
                fontSize: "0.92rem",
                boxShadow: "0 4px 14px rgba(255, 214, 10, 0.3)"
              }}
            >
              {busyScript ? "⏳ Generating Script..." : "📝 Action 4.1: Generate Master Script & Blueprint"}
            </button>
            <button
              type="button"
              className="btn"
              disabled={busyAudio}
              onClick={synthesizeVoiceAndLivePlayer}
              style={{
                background: "linear-gradient(135deg, #38bdf8 0%, #0284c7 100%)",
                color: "#fff",
                fontWeight: 800,
                padding: "12px 20px",
                fontSize: "0.92rem",
                boxShadow: "0 4px 14px rgba(56, 189, 248, 0.35)"
              }}
            >
              {busyAudio ? "🎙️ Synthesizing Voice..." : "▶️ Action 4.2: Synthesize Voice & Live Play Video"}
            </button>
          </div>
        </div>
      </section>

      {/* STEP 5: Master Blueprint Inspector & AWS Bedrock Token Telemetry */}
      {blueprint && (
        <section className="card" style={{
          background: "linear-gradient(180deg, var(--panel) 0%, rgba(12, 12, 18, 0.99) 100%)",
          border: "1px solid rgba(56, 189, 248, 0.4)",
          boxShadow: "0 25px 70px rgba(0,0,0,0.85)",
          marginBottom: 24
        }}>
          {/* Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 14, marginBottom: 16 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <span className="badge ok">✓ Step 5: Master Blueprint Ready</span>
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
                  {busyAudio ? "Synthesizing Audio..." : "▶️ Action 5.X: Synthesize Voice & Live Player"}
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

          {/* Official AWS Bedrock Token & Cost Telemetry Widget */}
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
                    📊 Official AWS Bedrock Telemetry:
                  </span>
                  <span className="badge" style={{ background: "rgba(255, 214, 10, 0.15)", color: "#ffd60a" }}>
                    {blueprint.token_telemetry.model_name}
                  </span>
                  <span className="badge ok">
                    {blueprint.token_telemetry.vendor}
                  </span>
                </div>
                <div className="muted" style={{ fontSize: "0.74rem", marginTop: 2 }}>
                  Official token accounting calculated strictly via AWS Bedrock On-Demand pricing schedule.
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
                  <div style={{ fontSize: "0.68rem", color: "#30d158", fontWeight: 700 }}>CALCULATED COST</div>
                  <div style={{ fontWeight: 900, fontSize: "1.05rem", color: "#30d158" }}>
                    ${blueprint.token_telemetry.total_cost_usd.toFixed(4)} USD
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Sub-view Navigation Tabs */}
          <div className="tab-bar" style={{ marginBottom: 16 }}>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "storyboard" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("storyboard")}
              style={{ fontWeight: 700, color: activeInspectorTab === "storyboard" ? "#ffd60a" : undefined }}
            >
              5.1 📝 Master Script &amp; Choreography ({blueprint.scenes.length})
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "player" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("player")}
              style={{ fontWeight: 700, color: activeInspectorTab === "player" ? "#38bdf8" : undefined }}
            >
              5.2 ▶️ Theater Live Preview Player {blueprint.has_audio ? "✓" : "(Requires Voice Synthesis)"}
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "prompt" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("prompt")}
            >
              5.3 🤖 Multimodal AI Master Prompt
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "html" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("html")}
            >
              5.4 🌐 Standalone HTML5 Code
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "audio" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("audio")}
            >
              5.5 🎵 Film Audio Bus Scoring
            </button>
            <button
              type="button"
              className={`tab-btn ${activeInspectorTab === "raw" ? "active" : ""}`}
              onClick={() => setActiveInspectorTab("raw")}
            >
              5.6 ⚙️ Raw Blueprint JSON
            </button>
          </div>

          {/* Sub-view 5.1: Master Script & Storyboard Breakdown */}
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
                    Every scene is paced at 150 WPM with human inflections, camera dynamics, and B-roll cues. Click <strong>Action 4.2</strong> to synthesize real voice &amp; launch the interactive player.
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
                    {busyAudio ? "Synthesizing..." : "▶️ Launch Live Player (Action 4.2)"}
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
                        Scene {s.scene_number}: {s.title.includes(":") ? s.title.split(":")[1].trim() : s.title}
                      </span>
                      <span className="badge" style={{ fontSize: "0.72rem" }}>
                        {s.start_s}s - {s.end_s}s ({s.duration_s}s)
                      </span>
                    </div>

                    {/* Spoken Narration Dialogue */}
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

          {/* Sub-view 5.2: Theater Live Preview Player */}
          {activeInspectorTab === "player" && (
            <div>
              {!blueprint.has_audio ? (
                <div style={{
                  background: "rgba(56, 189, 248, 0.1)",
                  border: "1px solid #38bdf8",
                  borderRadius: 12,
                  padding: 24,
                  textAlign: "center"
                }}>
                  <h3 style={{ margin: "0 0 8px", color: "#38bdf8" }}>▶️ Live Player Requires Voice Synthesis</h3>
                  <p className="muted" style={{ margin: "0 0 16px", maxWidth: 600, marginLeft: "auto", marginRight: "auto" }}>
                    Your master script is generated! Click below to synthesize your chosen voice ({selectedVoiceId}), calculate word-by-word timestamps, and build your interactive stage.
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

                  {/* Theater Stage Layout */}
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

                    {/* Director Teleprompter (for 9:16 vertical mode) */}
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

          {/* Sub-view 5.3: Multimodal AI Master Prompt */}
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

          {/* Sub-view 5.4: Standalone HTML Code */}
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
                {blueprint.standalone_html_code || "Execute Action 4.2 to generate standalone HTML player code."}
              </pre>
            </div>
          )}

          {/* Sub-view 5.5: Film Audio Bus */}
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

          {/* Sub-view 5.6: Raw JSON */}
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

      {/* STEP 7: Final MP4 Video Render & Workspace Asset Hub */}
      {blueprint && (
        <section className="card" style={{ background: "rgba(12, 14, 22, 0.95)", border: "1px solid var(--line)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12, flexWrap: "wrap", gap: 10 }}>
            <div>
              <h3 style={{ margin: 0, fontSize: "1.12rem" }}>Step 7: Final MP4 Video Render &amp; Export Hub</h3>
              <p className="muted" style={{ margin: "2px 0 0", fontSize: "0.82rem" }}>
                Render your final video directly on your local system with synchronized neural voice, animated SVG graphics, and copyright-free audio bus.
              </p>
            </div>
            {/* Step 7 Render MP4 Button */}
            <button
              type="button"
              className="btn"
              disabled={renderingMp4 || !blueprint.html_file}
              onClick={renderFinalMp4}
              style={{
                background: renderedMp4Result ? "#30d158" : "linear-gradient(135deg, #e11d48 0%, #be123c 100%)",
                color: "#fff",
                fontWeight: 800,
                fontSize: "0.88rem",
                padding: "10px 18px",
                boxShadow: "0 4px 15px rgba(225, 29, 72, 0.4)"
              }}
            >
              {renderingMp4 ? "⏳ Rendering Local MP4..." : (renderedMp4Result ? "✓ MP4 Rendered Successfully!" : "🎬 Action 7.1: Render Final Local MP4 Video")}
            </button>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 12, marginTop: 14 }}>
            <div style={{ background: "var(--panel-alt)", padding: 12, borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontWeight: 700, fontSize: "0.85rem", color: "#38bdf8" }}>📄 Master Prompt File (.md)</div>
              <div className="muted" style={{ fontSize: "0.74rem", margin: "4px 0" }}>Portable prompt for Gemini, ChatGPT, Claude</div>
              <button type="button" className="secondary" onClick={downloadPromptFile} style={{ fontSize: "0.72rem", padding: "4px 8px", marginTop: 4 }}>
                💾 Download .md File
              </button>
            </div>

            <div style={{ background: "var(--panel-alt)", padding: 12, borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontWeight: 700, fontSize: "0.85rem", color: "#ffd60a" }}>🌐 HTML5 Player Standalone (.html)</div>
              <div className="muted" style={{ fontSize: "0.74rem", margin: "4px 0" }}>Offline playable canvas animation bundle</div>
              <button type="button" className="secondary" disabled={!blueprint.standalone_html_code} onClick={downloadHtmlFile} style={{ fontSize: "0.72rem", padding: "4px 8px", marginTop: 4 }}>
                {blueprint.standalone_html_code ? "💾 Download .html Player" : "Pending Action 4.2"}
              </button>
            </div>

            <div style={{ background: "var(--panel-alt)", padding: 12, borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontWeight: 700, fontSize: "0.85rem", color: "#30d158" }}>🎬 Final Rendered MP4 Video (.mp4)</div>
              <div className="muted" style={{ fontSize: "0.74rem", margin: "4px 0" }}>Broadcast-grade 1080p video file on disk</div>
              {renderedMp4Result ? (
                <a href={renderedMp4Result.download_url} download={renderedMp4Result.filename} className="btn ok" style={{ fontSize: "0.75rem", padding: "6px 12px", display: "inline-block", marginTop: 4, textDecoration: "none", fontWeight: 800 }}>
                  ⬇️ Download {renderedMp4Result.filename}
                </a>
              ) : (
                <button type="button" className="secondary" disabled={renderingMp4 || !blueprint.html_file} onClick={renderFinalMp4} style={{ fontSize: "0.72rem", padding: "4px 8px", marginTop: 4 }}>
                  {renderingMp4 ? "Rendering..." : "🎬 Execute Action 7.1 Render"}
                </button>
              )}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
