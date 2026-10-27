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
  file: string;
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
