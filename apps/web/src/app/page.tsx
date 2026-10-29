"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, ACTIVE, API, type Health, type Job, type NicheCategory, type Project } from "@/lib/api";

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [skills, setSkills] = useState<NicheCategory[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    const load = async () => {
      try {
        const [p, j] = await Promise.all([api.projects(), api.jobs()]);
        if (live) {
          setProjects(p);
          setJobs(j);
          setError(null);
        }
      } catch (e) {
        const msg = (e as Error).message || "";
        if (live && projects.length === 0 && !msg.includes("Failed to fetch")) {
          setError(`Cannot reach the API (${msg}). Start it with: python scripts/dev.py`);
        }
      }
    };
    load();
    api.health(true).then(setHealth).catch(() => {});
    api.getSettings().then(res => {
      if (res.niche_categories && live) setSkills(res.niche_categories);
    }).catch(() => {});
    const t = setInterval(load, 2000);
    return () => {
      live = false;
      clearInterval(t);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const title = (id: string) => projects.find(p => p.id === id)?.title ?? id;
  const running = jobs.filter(j => ACTIVE.includes(j.state));
  const failed = jobs.filter(j => j.state === "failed");
  const exportsList = projects.filter(p => p.status === "completed" || p.has_export);

  return (
    <>
      <div className="card" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 16, background: "linear-gradient(135deg, var(--panel) 0%, var(--panel-alt) 100%)" }}>
        <div>
          <h1 style={{ margin: 0 }}>Dashboard</h1>
          <p className="muted" style={{ margin: "4px 0 0" }}>
            Welcome to AIVideoStudio — Create professional AI-directed educational & documentary videos effortlessly.
          </p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <Link className="btn" href="/projects/new">+ Create project</Link>
          <Link className="btn secondary" href="/settings?tab=effectcraft">MCP & Engine Status</Link>
        </div>
      </div>

      {error && <div role="alert" className="error">{error}</div>}

      <div className="kpi-grid">
        <div className="kpi-card">
          <div>
            <div className="kpi-label">Total Projects</div>
            <div className="kpi-value">{projects.length}</div>
          </div>
          <div className="kpi-icon">▤</div>
        </div>
        <div className="kpi-card">
          <div>
            <div className="kpi-label">Running Jobs</div>
            <div className="kpi-value" style={{ color: running.length > 0 ? "var(--warn)" : "var(--text)" }}>{running.length}</div>
          </div>
          <div className="kpi-icon" style={{ background: "var(--warn-soft)", color: "var(--warn)" }}>⚡</div>
        </div>
        <div className="kpi-card">
          <div>
            <div className="kpi-label">Completed Exports</div>
            <div className="kpi-value" style={{ color: "var(--ok)" }}>{exportsList.length}</div>
          </div>
          <div className="kpi-icon" style={{ background: "var(--ok-soft)", color: "var(--ok)" }}>▶</div>
        </div>
        <div className="kpi-card">
          <div>
            <div className="kpi-label">Failed Jobs</div>
            <div className="kpi-value" style={{ color: failed.length > 0 ? "var(--bad)" : "var(--text)" }}>{failed.length}</div>
          </div>
          <div className="kpi-icon" style={{ background: "var(--bad-soft)", color: "var(--bad)" }}>!</div>
        </div>
      </div>

      {skills.length > 0 && (
        <section className="card" aria-label="Production Archetype Skills" style={{ marginBottom: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12, flexWrap: "wrap", gap: 8 }}>
            <div>
              <h2 style={{ margin: 0, fontSize: "1.15rem" }}>⚡ Production Archetype Skills</h2>
              <p className="muted" style={{ margin: "2px 0 0", fontSize: ".82rem" }}>
                Locked cinematic rule sets (`SKILL.md`) driving AI Director storyboard typography, camera clamping, and vector layer rendering.
              </p>
            </div>
            <Link href="/projects/new" className="badge ok" style={{ textDecoration: "none" }}>
              {skills.length} Skills Active →
            </Link>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: 10 }}>
            {skills.map(sk => (
              <div
                key={sk.id}
                style={{
                  background: "var(--panel-alt)",
                  border: "1px solid var(--line)",
                  borderRadius: 10,
                  padding: "10px 12px",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                }}
              >
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                    <span className="badge ok" style={{ fontSize: ".72rem" }}>{sk.badge}</span>
                    <span className="muted" style={{ fontSize: ".72rem" }}>{sk.default_aspect_ratio}</span>
                  </div>
                  <div style={{ fontWeight: 600, fontSize: ".88rem", marginBottom: 3 }}>{sk.name}</div>
                  <div className="muted" style={{ fontSize: ".76rem", marginBottom: 6 }}>{sk.reference_style}</div>
                  <p className="muted" style={{ fontSize: ".76rem", margin: "0 0 10px", lineHeight: 1.35, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                    {sk.description}
                  </p>
                </div>
                <div style={{ display: "flex", gap: 6 }}>
                  <Link
                    href={`/projects/new?skill=${sk.id}&sample=1`}
                    className="btn secondary"
                    style={{ flex: 1, textAlign: "center", fontSize: ".76rem", padding: "5px 8px" }}
                  >
                    Sample
                  </Link>
                  <Link
                    href={`/projects/new?skill=${sk.id}`}
                    className="btn"
                    style={{ flex: 1, textAlign: "center", fontSize: ".76rem", padding: "5px 8px" }}
                  >
                    Use Skill
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="grid-2">
        <div>
          <section className="card" aria-label="Recent projects">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
              <h2 style={{ margin: 0 }}>Recent Projects</h2>
              <Link href="/projects" style={{ fontSize: "0.84rem" }}>View All →</Link>
            </div>
            {projects.length === 0 ? (
              <p className="muted">No projects yet. Click Create project to start your first video.</p>
            ) : (
              <ul className="plain">
                {projects.slice(0, 8).map(p => (
                  <li key={p.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 14 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 12, minWidth: 0 }}>
                      <div
                        style={{
                          width: 84,
                          height: 48,
                          borderRadius: 7,
                          background: "#090d1a",
                          border: "1px solid var(--line)",
                          overflow: "hidden",
                          flexShrink: 0,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        {p.thumbnail ? (
                          <img src={`${API}${p.thumbnail}`} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                        ) : (
                          <span className="muted" style={{ fontSize: "0.72rem" }}>{p.settings.aspect_ratio}</span>
                        )}
                      </div>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                          <Link href={`/projects/${p.id}`} style={{ fontWeight: 600, color: "var(--text)" }}>{p.title}</Link>
                          <span className={`badge ${p.status === "completed" ? "ok" : ACTIVE.includes(p.status) ? "active" : ""}`}>
                            {p.status}
                          </span>
                          {p.token_usage?.used_api_tokens && (
                            <span className="badge ok" title={`Model: ${p.token_usage.primary_model_id} (${p.token_usage.total_input_tokens} in / ${p.token_usage.total_output_tokens} out)`}>
                              🪙 {p.token_usage.total_tokens.toLocaleString()} tok · ${p.token_usage.total_cost_usd.toFixed(4)}
                            </span>
                          )}
                        </div>
                        <div className="muted" style={{ fontSize: "0.79rem", marginTop: 2 }}>
                          {p.settings.aspect_ratio} · {p.settings.fps} fps · ~{p.settings.target_duration_s}s · {p.settings.narration?.voice || "kokoro:am_michael"} · {new Date(p.created_at).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                      <Link href={`/projects/${p.id}`} className="btn secondary" style={{ padding: "5px 11px", fontSize: "0.8rem" }}>
                        Open
                      </Link>
                      {p.has_export && (
                        <a href={api.mediaUrl(p.id, "renders/final.mp4", true)} className="btn" style={{ padding: "5px 11px", fontSize: "0.8rem" }}>
                          MP4
                        </a>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="card" aria-label="Completed exports">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <h2 style={{ margin: 0 }}>Completed Exports</h2>
              <Link href="/exports" style={{ fontSize: "0.84rem" }}>All Exports →</Link>
            </div>
            {exportsList.length === 0 ? (
              <p className="muted">No completed video exports yet.</p>
            ) : (
              <ul className="plain">
                {exportsList.slice(0, 6).map(p => (
                  <li key={p.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                    <div>
                      <Link href={`/projects/${p.id}`} style={{ fontWeight: 600 }}>{p.title}</Link>{" "}
                      <span className="badge ok">MP4 Ready</span>{" "}
                      {p.token_usage?.used_api_tokens && (
                        <span className="badge">${p.token_usage.total_cost_usd.toFixed(4)} USD ({p.token_usage.total_tokens.toLocaleString()} tok)</span>
                      )}{" "}
                      <span className="muted" style={{ fontSize: "0.8rem" }}>({p.settings.aspect_ratio})</span>
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                      <a href={api.mediaUrl(p.id, "renders/final.mp4", true)} className="btn secondary" style={{ padding: "4px 10px", fontSize: "0.78rem" }}>
                        Download MP4
                      </a>
                      <a href={api.exportZipUrl(p.id)} className="btn secondary" style={{ padding: "4px 10px", fontSize: "0.78rem" }}>
                        ZIP
                      </a>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>

        <div>
          <section className="card" aria-label="Current jobs">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <h2 style={{ margin: 0 }}>Current Jobs</h2>
              <Link href="/jobs" style={{ fontSize: "0.84rem" }}>Job Monitor →</Link>
            </div>
            {running.length === 0 ? (
              <p className="muted">No jobs running right now.</p>
            ) : (
              <ul className="plain">
                {running.map(j => {
                  const pct = j.progress_total ? Math.round((j.progress_done / j.progress_total) * 100) : 20;
                  return (
                    <li key={j.id}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                        <Link href={`/projects/${j.project_id}`} style={{ fontWeight: 600 }}>{title(j.project_id)}</Link>
                        <span className="badge active">{j.state} ({pct}%)</span>
                      </div>
                      <div className="muted" style={{ fontSize: "0.82rem", marginBottom: 6 }}>
                        {j.kind} — {j.current_step || "Processing..."}
                      </div>
                      <progress value={j.progress_done} max={j.progress_total || 100} />
                    </li>
                  );
                })}
              </ul>
            )}
          </section>

          <section className="card" aria-label="Failed jobs">
            <h2>Needs Attention</h2>
            {failed.length === 0 ? (
              <p className="muted">No failed jobs.</p>
            ) : (
              <ul className="plain">
                {failed.slice(0, 5).map(j => (
                  <li key={j.id}>
                    <Link href={`/projects/${j.project_id}`} style={{ fontWeight: 600 }}>{title(j.project_id)}</Link>
                    <div className="muted" style={{ fontSize: "0.82rem", color: "var(--bad)" }}>{j.error}</div>
                  </li>
                ))}
              </ul>
            )}
          </section>

          {health && (
            <section className="card" aria-label="System health">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <h2 style={{ margin: 0 }}>System Health & MCP Engines</h2>
                <Link href="/settings?tab=effectcraft" style={{ fontSize: "0.8rem" }}>Configure & Test →</Link>
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 10 }}>
                {Object.entries(health.tools).map(([k, v]) => (
                  <span key={k} title={v.fix ?? v.detail} className={`badge ${v.ok ? "ok" : "bad"}`}>
                    {k}: {v.ok ? "ok" : "missing"}
                  </span>
                ))}
              </div>
              <p className="muted" style={{ fontSize: "0.8rem", margin: 0 }}>
                EffectCraft v0.17.0 & FilmCraft v0.13.0 are installed locally and connected via headless stdio MCP. No manual operation required.
              </p>
            </section>
          )}
        </div>
      </div>
    </>
  );
}
