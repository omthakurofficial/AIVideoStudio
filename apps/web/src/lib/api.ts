export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type Settings = {
  aspect_ratio: "16:9" | "9:16"; fps: number; target_duration_s: number; visual_style: string;
  approval_mode: "manual" | "automatic";
  narration: { mode: "none" | "user_audio" | "generate"; voice: string | null };
  captions: { enabled: boolean; font_size: number };
  topic: string | null; reference_description: string | null;
};
export type Project = { id: string; title: string; status: string; settings: Settings; created_at: string; updated_at: string;
  output?: { width: number; height: number; fps: number }; script?: string };
export type Job = { id: string; project_id: string; kind: string; state: string; progress_done: number; progress_total: number | null;
  current_step: string | null; error: string | null; created_at: string; updated_at: string; logs?: { ts: string; level: string; message: string }[] };
export type Health = { ok: boolean; tools: Record<string, { ok: boolean; detail: string; fix?: string }>; aws?: { ok: boolean; detail: string } };

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API}${path}`, { ...init, cache: "no-store", headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) } });
  if (!r.ok) {
    let msg = `${r.status} ${r.statusText}`;
    try { const b = await r.json(); msg = typeof b.detail === "string" ? b.detail : JSON.stringify(b.detail); } catch {}
    throw new Error(msg);
  }
  return r.json();
}
export const api = {
  health: () => req<Health>("/api/health"),
  projects: () => req<Project[]>("/api/projects"),
  project: (id: string) => req<Project>(`/api/projects/${id}`),
  createProject: (b: { title: string; script: string; settings: Partial<Settings> }) => req<Project>("/api/projects", { method: "POST", body: JSON.stringify(b) }),
  saveScript: (id: string, script: string) => req(`/api/projects/${id}/script`, { method: "PUT", body: JSON.stringify({ script }) }),
  analyze: (id: string) => req<Job>(`/api/projects/${id}/jobs/analyze`, { method: "POST" }),
  jobs: (projectId?: string) => req<Job[]>(`/api/jobs${projectId ? `?project_id=${projectId}` : ""}`),
  job: (id: string) => req<Job>(`/api/jobs/${id}`),
  retry: (id: string) => req<Job>(`/api/jobs/${id}/retry`, { method: "POST" }),
  cancel: (id: string) => req<Job>(`/api/jobs/${id}/cancel`, { method: "POST" }),
};
export const ACTIVE = ["queued","analyzing","planning","awaiting_approval","generating_assets","generating_narration","rendering_scenes","assembling","quality_check"];
