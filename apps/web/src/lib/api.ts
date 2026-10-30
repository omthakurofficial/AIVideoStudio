export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type Settings = {
  aspect_ratio: "16:9" | "9:16";
  fps: number;
  target_duration_s: number;
  visual_style: string;
  approval_mode: "manual" | "automatic";
  narration: { mode: "none" | "user_audio" | "generate"; voice: string | null };
  captions: { enabled: boolean; font_size: number };
  topic: string | null;
  reference_description: string | null;
  ai_model?: string | null;
  niche_category?: string | null;
};

export type NicheCategory = {
  id: string;
  name: string;
  badge: string;
  reference_style: string;
  default_visual_style: string;
  default_aspect_ratio: "16:9" | "9:16";
  description: string;
  director_rules: string;
  sample_title: string;
  sample_topic: string;
  sample_script: string;
};

export type ArchitectureLayer = {
  layer: number;
  title: string;
  description: string;
  options: { id: string; name: string; cost: string; mode: string }[];
};

export type ModelCatalogItem = {
  model_id: string;
  label: string;
  vendor: string;
  family: string;
  region_scope: string;
  input_per_1m_usd: number;
  output_per_1m_usd: number;
  official_pricing_url: string;
  supports_tool_use: boolean;
  recommended_for: string[];
};

export type OfficialPricingLink = {
  name: string;
  url: string;
  note: string;
};

export type VoiceOption = {
  id: string;
  label: string;
  provider: string;
  cost_usd: number;
};

export type TokenCallRecord = {
  stage: string;
  provider: string;
  model_id: string;
  model_label: string;
  vendor: string;
  attempts: number;
  latency_s: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  input_rate_per_1m_usd: number;
  output_rate_per_1m_usd: number;
  input_cost_usd: number;
  output_cost_usd: number;
  total_cost_usd: number;
  official_pricing_url: string;
  bedrock_pricing_url: string;
  ts?: string;
};

export type TokenUsageReport = {
  used_api_tokens: boolean;
  provider: string;
  primary_model_id: string | null;
  primary_model_label: string | null;
  calls: TokenCallRecord[];
  total_input_tokens: number;
  total_output_tokens: number;
  total_tokens: number;
  total_cost_usd: number;
  tts_cost_usd: number;
  rendering_cost_usd: number;
  official_pricing_links: OfficialPricingLink[];
};

export type ScriptAnalysis = {
  paragraph_count: number;
  total_words: number;
  estimated_seconds: number;
  recommended_target_duration_s: number;
  detected_format: string;
  recommended_aspect_ratio: "16:9" | "9:16";
  aspect_reason: string;
  clean_narration: string;
  visual_hints: string[];
  paragraphs: {
    index: number;
    words: number;
    sentences: number;
    estimated_seconds: number;
    heading?: string | null;
    visual_hint?: string | null;
    narration?: string;
  }[];
};

export type SampleScript = {
  id: string;
  title: string;
  file?: string;
  niche_category?: string;
  aspect_ratio: "16:9" | "9:16";
  visual_style: string;
  category: string;
  script: string;
  analysis: {
    scene_count: number;
    total_words: number;
    estimated_seconds: number;
    recommended_target_duration_s: number;
    detected_format: string;
  };
};

export type SupportedFormat = { id: string; name: string; description: string; example: string };

export type Project = {
  id: string;
  title: string;
  status: string;
  settings: Settings;
  created_at: string;
  updated_at: string;
  output?: { width: number; height: number; fps: number };
  script?: string;
  has_export?: boolean;
  thumbnail?: string | null;
  script_analysis?: ScriptAnalysis;
  token_usage?: TokenUsageReport;
};

export type Job = {
  id: string;
  project_id: string;
  project_title?: string;
  kind: string;
  state: string;
  progress_done: number;
  progress_total: number | null;
  current_step: string | null;
  error: string | null;
  checkpoint?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  logs?: { ts: string; level: string; message: string }[];
};

export type ToolHealth = {
  ok: boolean;
  detail: string;
  fix?: string;
  binary_path?: string;
  installed?: boolean;
  mcp_mode?: string;
  mcp_needed?: boolean;
  role?: string;
};

export type Health = {
  ok: boolean;
  tools: Record<string, ToolHealth>;
  stock?: { ok: boolean; pexels_configured: boolean; pixabay_configured: boolean; detail: string };
  director?: { ok: boolean; detail: string };
  aws?: { ok: boolean; detail: string; region?: string; fix?: string };
};

export type EngineVerifyReport = {
  ok: boolean;
  tools: Record<string, ToolHealth>;
  stock: { ok: boolean; pexels_configured: boolean; pixabay_configured: boolean; detail: string };
  aws: { ok: boolean; detail: string; region?: string; fix?: string };
  mcp: {
    effectcraft?: {
      ok: boolean;
      version?: string;
      binary_path: string;
      transport?: string;
      tool_count?: number;
      tools?: string[];
      missing_tools?: string[];
      missing_commands?: string[];
      render_mode?: string;
      error?: string;
    };
    filmcraft?: {
      ok: boolean;
      version?: string;
      binary_path: string;
      transport?: string;
      tool_count?: number;
      tools?: string[];
      missing_tools?: string[];
      missing_commands?: string[];
      export_mode?: string;
      error?: string;
    };
  };
};

export type AppSettingsResponse = {
  preferences: {
    theme: "dark" | "light";
    accent_color: "blue" | "purple";
    default_aspect_ratio: "16:9" | "9:16";
    default_fps: number;
    default_visual_style: string;
    default_approval_mode: "automatic" | "manual";
    default_voice: string;
    captions_enabled: boolean;
    caption_font_size: number;
    caption_style: string;
  };
  models: Record<string, { provider: string; model_id: string; max_tokens?: number; temperature?: number }>;
  model_catalog?: ModelCatalogItem[];
  niche_categories?: NicheCategory[];
  architecture_layers?: ArchitectureLayer[];
  official_pricing_links?: OfficialPricingLink[];
  available_voices?: VoiceOption[];
  stock_media?: {
    pexels_configured: boolean;
    pexels_masked: string;
    pixabay_configured: boolean;
    pixabay_masked: string;
    wikimedia_enabled: boolean;
  };
  director: Record<string, any>;
  storage: { projects_dir: string; data_dir: string; db_path: string };
  engines: { effectcraft_cli: string; filmcraft_cli: string; ffmpeg: string; ffprobe: string; aws_region: string };
  health: Health;
};

export type WorkspaceFile = {
  path: string;
  name: string;
  folder: string;
  kind: "video" | "audio" | "image" | "project" | "json" | "text" | "binary";
  size_bytes: number;
  modified_at: string;
  url: string;
};

export type WorkspaceFilesResponse = {
  workspace_path: string;
  files: WorkspaceFile[];
  preview_content: string | null;
};

export type SceneT = {
  id: string;
  order: number;
  narration_text: string;
  estimated_duration: number;
  learning_objective: string;
  key_message: string;
  visual_type: string;
  visual_description: string;
  status: string;
  director_notes: string;
  visual_elements: { id: string; kind: string; label: string; props?: Record<string, any> }[];
  element_relationships: { source: string; target: string; kind: string }[];
  animation_sequence: { id: string; at: number; duration: number; action: string; targets: string[]; description: string }[];
  on_screen_text: { text: string; at: number; duration: number }[];
  asset_requirements: { id: string; kind: string; query: string; status: string; justification: string }[];
  transition: { type: string; duration: number };
  timing: { narration_audio_s: number | null; revised_from_audio: boolean };
  quality_checks: string[];
  [k: string]: unknown;
};

export type StoryboardT = {
  schema_version: number;
  project_id: string;
  title: string;
  revision: number;
  approved: boolean;
  created_by: Record<string, unknown>;
  scenes: SceneT[];
};

export type ProjectReports = {
  workspace_path: string;
  quality_report?: {
    ok: boolean;
    output_mp4: string;
    passed_checks: string[];
    failed_checks: string[];
    scenes: {
      scene_id: string;
      ok: boolean;
      version: number;
      mp4_path: string;
      preview_png: string | null;
      duration_s: number;
      passed_checks: string[];
      failed_checks: string[];
      warnings: string[];
    }[];
    repairs_applied: {
      scene_id: string;
      failed_version: number;
      repaired_version: number;
      category: string;
      original_error: string;
      repair_applied: string;
      outcome: string;
    }[];
    limitations: string[];
  };
  director_usage?: { model_id: string; input_tokens: number; output_tokens: number; latency_s: number; attempts: number };
  token_usage?: TokenUsageReport;
  asset_discovery?: {
    assets: {
      req_id: string;
      scene_id: string;
      status: string;
      local_rel_path: string | null;
      provider: string | null;
      external_id: string | null;
      source_url: string | null;
      licence: string | null;
      note: string;
    }[];
  };
  caption_validation?: { ok: boolean; caption_count: number; issues: string[] };
  manifest?: { version: number; assets: { path: string; kind: string; created_at: string; provenance: Record<string, any> }[] };
};

export const VISUAL_TYPES = [
  "animated_diagram",
  "architecture",
  "map",
  "chart",
  "timeline",
  "icons_labels",
  "footage",
  "screenshot",
  "ui_demo",
  "layered_motion",
  "hybrid",
];
export const TRANSITIONS = ["cut", "fade", "dissolve", "wipe", "slide"];
export const ACTIVE = [
  "queued",
  "analyzing",
  "planning",
  "awaiting_approval",
  "generating_assets",
  "generating_narration",
  "rendering_scenes",
  "assembling",
  "quality_check",
];

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API}${path}`, {
    ...init,
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!r.ok) {
    let msg = `${r.status} ${r.statusText}`;
    try {
      const b = await r.json();
      msg = typeof b.detail === "string" ? b.detail : JSON.stringify(b.detail);
    } catch {}
    throw new Error(msg);
  }
  return r.json();
}

export const api = {
  health: (aws = false) => req<Health>(`/api/health${aws ? "?aws=true" : ""}`),
  verifyEngines: () => req<EngineVerifyReport>("/api/engines/verify", { method: "POST" }),
  getSettings: () => req<AppSettingsResponse>("/api/settings"),
  saveSettings: (body: Record<string, any>) => req<{ ok: boolean; preferences: AppSettingsResponse["preferences"] }>("/api/settings", { method: "PUT", body: JSON.stringify(body) }),
  scriptSamples: () => req<{ samples: SampleScript[]; supported_formats: SupportedFormat[] }>("/api/scripts/samples"),
  inspectScript: (script: string) => req<ScriptAnalysis>("/api/scripts/inspect", { method: "POST", body: JSON.stringify({ script }) }),
  projects: () => req<Project[]>("/api/projects"),
  project: (id: string) => req<Project>(`/api/projects/${id}`),
  createProject: (b: { title: string; script: string; settings: Partial<Settings> }) =>
    req<Project>("/api/projects", { method: "POST", body: JSON.stringify(b) }),
  saveScript: (id: string, script: string) => req(`/api/projects/${id}/script`, { method: "PUT", body: JSON.stringify({ script }) }),
  generateScript: (id: string, topic: string, target_duration_s: number) =>
    req<{ ok: boolean; script: string }>(`/api/projects/${id}/generate-script`, { method: "POST", body: JSON.stringify({ topic, target_duration_s }) }),
  analyze: (id: string) => req<Job>(`/api/projects/${id}/jobs/analyze`, { method: "POST" }),
  produce: (id: string) => req<Job>(`/api/projects/${id}/jobs/produce`, { method: "POST" }),
  updateScene: (id: string, sceneId: string, body: Record<string, any>) =>
    req<StoryboardT>(`/api/projects/${id}/scenes/${sceneId}`, { method: "PUT", body: JSON.stringify(body) }),
  regenerateScene: (id: string, sceneId: string, body: { visual_correction?: string; visual_type?: string; visual_description?: string }) =>
    req<Job>(`/api/projects/${id}/scenes/${sceneId}/regenerate`, { method: "POST", body: JSON.stringify(body) }),
  reports: (id: string) => req<ProjectReports>(`/api/projects/${id}/reports`),
  projectFiles: (id: string, preview?: string) =>
    req<WorkspaceFilesResponse>(`/api/projects/${id}/files${preview ? `?preview=${encodeURIComponent(preview)}` : ""}`),
  exportZipUrl: (id: string) => `${API}/api/projects/${id}/export-zip`,
  mediaUrl: (id: string, relPath: string, download = false) =>
    `${API}/api/projects/${id}/media/${relPath}${download ? "?download=true" : ""}`,
  jobs: (projectId?: string) => req<Job[]>(`/api/jobs${projectId ? `?project_id=${projectId}` : ""}`),
  job: (id: string) => req<Job>(`/api/jobs/${id}`),
  retry: (id: string) => req<Job>(`/api/jobs/${id}/retry`, { method: "POST" }),
  cancel: (id: string) => req<Job>(`/api/jobs/${id}/cancel`, { method: "POST" }),

  // V2 Templates Studio API
  v2Niches: () => req<{ niches: V2NicheItem[]; voices: V2VoiceItem[]; models?: V2BedrockModelItem[]; max_duration_s: number }>("/api/v2/templates/niches"),
  v2GenerateTemplate: (body: {
    topic: string;
    niche_id: string;
    target_duration_s: number;
    aspect_ratio: string;
    mode: string;
    voice_id?: string;
    model_id?: string;
    synthesize_audio?: boolean;
    custom_instructions?: string;
  }) => req<V2TemplateBlueprint>("/api/v2/templates/generate", { method: "POST", body: JSON.stringify(body) }),
  v2SynthesizePlayer: (body: {
    topic: string;
    niche_id: string;
    target_duration_s: number;
    aspect_ratio: string;
    mode: string;
    voice_id?: string;
    model_id?: string;
    custom_instructions?: string;
  }) => req<V2TemplateBlueprint>("/api/v2/templates/synthesize-player", { method: "POST", body: JSON.stringify(body) }),
  v2SavePreviewHtml: (html: string) => req<{ ok: boolean; url: string }>("/api/v2/templates/render-html-preview", { method: "POST", body: JSON.stringify({ html }) }),
  v2RenderMp4: (body: { html_file: string; master_wav: string; aspect_ratio: string }) =>
    req<{ ok: boolean; mp4_file: string; filename: string; download_url: string }>("/api/v2/templates/render-mp4", { method: "POST", body: JSON.stringify(body) }),
};

export type V2BedrockModelItem = {
  id: string;
  name: string;
  vendor: string;
  badge: string;
  input_cost_per_1m: number;
  output_cost_per_1m: number;
  speed: string;
  description: string;
};

export type V2TokenTelemetry = {
  provider: string;
  model_id: string;
  model_label: string;
  model_name: string;
  vendor: string;
  family: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  input_cost_usd: number;
  output_cost_usd: number;
  total_cost_usd: number;
  latency_ms?: number;
  official_pricing_url: string;
};

export type V2VoiceItem = {
  id: string;
  name: string;
  label: string;
  provider: string;
  cost_usd: number;
  gender?: "male" | "female";
  accent?: string;
};

export type V2NicheItem = {
  id: string;
  name: string;
  category: string;
  badge: string;
  reference_channels: string;
  description: string;
  colors: { bg: string; accent: string; secondary: string; highlight: string; panel: string };
  typography: { display: string; body: string; accent: string };
  visual_elements: string[];
  music_style: string;
  default_aspect: "9:16" | "16:9";
  sample_topics: string[];
};

export type V2SceneBlueprint = {
  scene_number: number;
  title: string;
  start_s: number;
  end_s: number;
  duration_s: number;
  target_word_count: number;
  spoken_narration?: string;
  narration_guidance: string;
  character_acting: string;
  visual_choreography: string;
  broll_layers: string;
  camera_move: string;
  transition_out: string;
  sound_effects: string;
};

export type V2TemplateBlueprint = {
  status: string;
  project_title: string;
  niche: V2NicheItem;
  target_duration_s: number;
  target_word_count: number;
  aspect_ratio: string;
  mode: string;
  voice_id?: string;
  scenes: V2SceneBlueprint[];
  music_bus: {
    genre: string;
    sidechain_ducking: string;
    master_lufs: number;
  };
  portable_master_prompt: string;
  standalone_html_code?: string;
  html_file?: string;
  master_wav?: string;
  master_mp3?: string;
  audio_base64?: string;
  has_audio?: boolean;
  token_telemetry?: V2TokenTelemetry;
  selected_model_id?: string;
  audio_error?: string;
};

export const sbApi = {
  plan: (id: string) => req<Job>(`/api/projects/${id}/jobs/storyboard`, { method: "POST" }),
  get: async (id: string): Promise<StoryboardT | null> => {
    try {
      return await req<StoryboardT>(`/api/projects/${id}/storyboard`);
    } catch (e) {
      if (/No storyboard/.test((e as Error).message)) return null;
      throw e;
    }
  },
  save: (id: string, sb: StoryboardT) => req<StoryboardT>(`/api/projects/${id}/storyboard`, { method: "PUT", body: JSON.stringify(sb) }),
  approve: (id: string) => req<StoryboardT>(`/api/projects/${id}/storyboard/approve`, { method: "POST" }),
};
