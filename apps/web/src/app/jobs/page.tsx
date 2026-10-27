"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, ACTIVE, type Job } from "@/lib/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [tab, setTab] = useState<"all" | "current" | "completed" | "failed">("all");
  const [search, setSearch] = useState("");

  const load = useCallback(() => {
    api.jobs().then(setJobs).catch(() => {});
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 2000);
    return () => clearInterval(t);
  }, [load]);

  const filtered = jobs.filter(j => {
    const q = search.toLowerCase();
    const matchText =
      (j.project_title ?? "").toLowerCase().includes(q) ||
      j.project_id.toLowerCase().includes(q) ||
      j.kind.toLowerCase().includes(q) ||
      (j.current_step ?? "").toLowerCase().includes(q);
    if (!matchText) return false;
    if (tab === "current") return ACTIVE.includes(j.state);
    if (tab === "completed") return j.state === "completed";
    if (tab === "failed") return j.state === "failed" || j.state === "cancelled";
    return true;
  });

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 16 }}>
        <div>
          <h1 style={{ margin: 0 }}>Jobs & Exports Monitor</h1>
          <p className="muted" style={{ margin: "2px 0 0" }}>
            Searchable production job history with real pipeline status, stage progress, timestamps, and failure recovery.
          </p>
        </div>
        <Link href="/projects/new" className="btn">+ Create Project</Link>
      </div>

      <section className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 14 }}>
          <div className="tab-bar" style={{ margin: 0, border: 0, padding: 0 }}>
            <button type="button" className={`tab-btn ${tab === "all" ? "active" : ""}`} onClick={() => setTab("all")}>
              All Jobs ({jobs.length})
            </button>
            <button type="button" className={`tab-btn ${tab === "current" ? "active" : ""}`} onClick={() => setTab("current")}>
              Current Jobs ({jobs.filter(j => ACTIVE.includes(j.state)).length})
            </button>
            <button type="button" className={`tab-btn ${tab === "completed" ? "active" : ""}`} onClick={() => setTab("completed")}>
              Completed ({jobs.filter(j => j.state === "completed").length})
            </button>
            <button type="button" className={`tab-btn ${tab === "failed" ? "active" : ""}`} onClick={() => setTab("failed")}>
              Failed ({jobs.filter(j => j.state === "failed" || j.state === "cancelled").length})
            </button>
          </div>
          <input
            placeholder="Search by project, stage, or job ID…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ maxWidth: 320 }}
          />
        </div>

        {filtered.length === 0 ? (
          <p className="muted">No jobs match the selected filter.</p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Project</th>
                  <th>Job Type</th>
                  <th>Current Stage / Detail</th>
                  <th>Progress</th>
                  <th>Started</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(j => {
                  const pct = j.progress_total ? Math.round((j.progress_done / j.progress_total) * 100) : j.state === "completed" ? 100 : 0;
                  return (
                    <tr key={j.id}>
                      <td>
                        <Link href={`/projects/${j.project_id}`} style={{ fontWeight: 600 }}>
                          {j.project_title || j.project_id}
                        </Link>
                      </td>
                      <td><code>{j.kind}</code></td>
                      <td>
                        <div>{j.current_step || "—"}</div>
                        {j.error && <div style={{ color: "var(--bad)", fontSize: "0.78rem", marginTop: 2 }}>{j.error}</div>}
                      </td>
                      <td style={{ minWidth: 140 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <progress value={j.progress_done} max={j.progress_total || 100} style={{ flex: 1 }} />
                          <span className="muted" style={{ fontSize: "0.76rem", width: 36 }}>{pct}%</span>
                        </div>
                      </td>
                      <td className="muted" style={{ fontSize: "0.8rem" }}>{new Date(j.created_at).toLocaleString()}</td>
                      <td>
                        <span className={`badge ${ACTIVE.includes(j.state) ? "active" : j.state}`}>
                          {j.state}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: "flex", gap: 6 }}>
                          <Link href={`/projects/${j.project_id}?tab=monitor`} className="btn secondary" style={{ padding: "4px 10px", fontSize: "0.78rem" }}>
                            Inspect
                          </Link>
                          {(j.state === "failed" || j.state === "cancelled") && (
                            <button
                              type="button"
                              style={{ padding: "4px 10px", fontSize: "0.78rem" }}
                              onClick={() => api.retry(j.id).then(load)}
                            >
                              Retry
                            </button>
                          )}
                          {ACTIVE.includes(j.state) && (
                            <button
                              type="button"
                              className="secondary"
                              style={{ padding: "4px 10px", fontSize: "0.78rem" }}
                              onClick={() => api.cancel(j.id).then(load)}
                            >
                              Cancel
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </>
  );
}
