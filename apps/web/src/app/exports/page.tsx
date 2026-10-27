"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { api, type Project } from "@/lib/api";

export default function ExportsPage() {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    api.projects().then(ps => setProjects(ps.filter(p => p.status === "completed" || p.has_export))).catch(() => {});
  }, []);

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12, marginBottom: 16 }}>
        <div>
          <h1 style={{ margin: 0 }}>Completed Video Exports</h1>
          <p className="muted" style={{ margin: "2px 0 0" }}>
            Preview and download finished H.264 MP4 videos, synchronized SRT captions, and full editable project packages (.ecproj + .fcproj).
          </p>
        </div>
        <Link href="/projects/new" className="btn">+ Create New Video</Link>
      </div>

      {projects.length === 0 ? (
        <section className="card">
          <p className="muted">No completed exports yet. Create a project and run automatic production to generate an MP4 export.</p>
        </section>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(420px, 1fr))", gap: 18 }}>
          {projects.map(p => (
            <section key={p.id} className="card" style={{ margin: 0 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
                <Link href={`/projects/${p.id}?tab=export`} style={{ fontWeight: 700, fontSize: "1.05rem", color: "var(--text)" }}>
                  {p.title}
                </Link>
                <span className="badge ok">MP4 Verified</span>
              </div>
              <video
                controls
                preload="metadata"
                poster={`${api.mediaUrl(p.id, "renders/previews/s01.png")}?t=${encodeURIComponent(p.updated_at)}`}
                src={`${api.mediaUrl(p.id, "renders/final.mp4")}?t=${encodeURIComponent(p.updated_at)}`}
                style={{ width: "100%", maxHeight: 280, background: "#000", borderRadius: 8, marginBottom: 10 }}
              />
              <div className="muted" style={{ fontSize: "0.82rem", marginBottom: 12 }}>
                Aspect: <strong>{p.settings.aspect_ratio}</strong> · {p.settings.fps} fps · Style: {p.settings.visual_style} · Updated {new Date(p.updated_at).toLocaleString()}
              </div>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <a className="btn" href={api.mediaUrl(p.id, "renders/final.mp4", true)}>
                  Download MP4
                </a>
                <a className="btn secondary" href={api.exportZipUrl(p.id)}>
                  Project Package (ZIP)
                </a>
                <a className="btn secondary" href={api.mediaUrl(p.id, "captions/captions.srt", true)}>
                  Captions (.srt)
                </a>
                <Link className="btn secondary" href={`/projects/${p.id}?tab=export`}>
                  Open Export Studio
                </Link>
              </div>
            </section>
          ))}
        </div>
      )}
    </>
  );
}
