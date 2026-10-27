"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, ACTIVE, type Health, type Job, type Project } from "@/lib/api";

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    const load = async () => {
      try {
        const [p, j] = await Promise.all([api.projects(), api.jobs()]);
        if (live) { setProjects(p); setJobs(j); setError(null); }
      } catch (e) { if (live) setError(`Cannot reach the API (${(e as Error).message}). Is it running? Start it with: python scripts/dev.py`); }
    };
    load(); api.health().then(setHealth).catch(() => {});
    const t = setInterval(load, 2000);
    return () => { live = false; clearInterval(t); };
  }, []);

  const title = (id: string) => projects.find(p => p.id === id)?.title ?? id;
  const running = jobs.filter(j => ACTIVE.includes(j.state));
  const failed = jobs.filter(j => j.state === "failed");
  return (
    <>
      <h1>Dashboard</h1>
      {error && <div role="alert" className="error">{error}</div>}
      <p><Link className="btn" href="/projects/new">Create project</Link></p>
      {health && (
        <section className="card" aria-label="System health">
          <h2>System health</h2>
          {Object.entries(health.tools).map(([k, v]) => (
            <span key={k} title={v.fix ?? v.detail} className={`badge ${v.ok ? "ok" : "bad"}`} style={{ marginRight: 8 }}>{k}: {v.ok ? "ok" : "missing"}</span>
          ))}
        </section>
      )}
      <section className="card" aria-label="Current jobs"><h2>Current jobs</h2>
        {running.length === 0 ? <p className="muted">No jobs running.</p> :
          <ul className="plain">{running.map(j => <li key={j.id}><Link href={`/projects/${j.project_id}`}>{title(j.project_id)}</Link> — {j.kind} <span className="badge active">{j.state}</span></li>)}</ul>}
      </section>
      <section className="card" aria-label="Failed jobs"><h2>Needs attention</h2>
        {failed.length === 0 ? <p className="muted">No failed jobs.</p> :
          <ul className="plain">{failed.map(j => <li key={j.id}><Link href={`/projects/${j.project_id}`}>{title(j.project_id)}</Link> — {j.error}</li>)}</ul>}
      </section>
      <section className="card" aria-label="Recent projects"><h2>Recent projects</h2>
        {projects.length === 0 ? <p className="muted">No projects yet.</p> :
          <ul className="plain">{projects.map(p => <li key={p.id}><Link href={`/projects/${p.id}`}>{p.title}</Link> <span className="muted">· {p.settings.aspect_ratio} · {p.settings.fps} fps · {new Date(p.created_at).toLocaleString()}</span></li>)}</ul>}
      </section>
    </>
  );
}
