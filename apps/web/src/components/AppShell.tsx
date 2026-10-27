"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { api, type Health } from "@/lib/api";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "◫" },
  { href: "/projects", label: "Projects", icon: "▤" },
  { href: "/projects/new", label: "Create Project", icon: "＋" },
  { href: "/jobs", label: "Jobs", icon: "⚡" },
  { href: "/exports", label: "Exports", icon: "▶" },
  { href: "/settings", label: "Settings", icon: "⚙" },
];

const WORKFLOW_STEPS = [
  "Script Input",
  "AI Analysis",
  "Storyboard",
  "Visual Planning",
  "Asset & Motion Gen",
  "Narration & Captions",
  "Assembly & QC",
  "Final Export",
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname() || "/";
  const [health, setHealth] = useState<Health | null>(null);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [accent, setAccent] = useState<"blue" | "purple">("blue");

  useEffect(() => {
    api.health(true).then(setHealth).catch(() => {});
    api.getSettings().then(s => {
      if (s.preferences?.theme) setTheme(s.preferences.theme);
      if (s.preferences?.accent_color) setAccent(s.preferences.accent_color);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.setAttribute("data-accent", accent);
  }, [theme, accent]);

  const ecOk = health?.tools?.effectcraft?.ok ?? true;
  const fcOk = health?.tools?.filmcraft?.ok ?? true;
  const awsOk = health?.aws?.ok ?? true;

  return (
    <div className="app-shell">
      <aside className="app-sidebar" aria-label="Sidebar">
        <div>
          <Link href="/" className="brand-box">
            <span className="brand-icon">▶</span>
            <div>
              <div>AIVideoStudio</div>
              <div style={{ fontSize: "0.7rem", fontWeight: 500, color: "#94a3b8" }}>AI Production Suite</div>
            </div>
          </Link>

          <nav className="sidebar-nav" aria-label="Main">
            {NAV_ITEMS.map(item => {
              const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
              return (
                <Link key={item.href} href={item.href} className={`nav-item ${active ? "active" : ""}`}>
                  <span style={{ width: 18, textAlign: "center" }}>{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              );
            })}
            <Link href="/projects/new" className="nav-item" style={{ fontSize: "0.82rem", opacity: 0.85 }}>
              <span style={{ width: 18, textAlign: "center" }}>✦</span>
              <span>New project</span>
            </Link>
          </nav>
        </div>

        <div className="sidebar-footer">
          <div style={{ fontWeight: 600, color: "#e2e8f0", marginBottom: 6 }}>MCP Engine Runtime</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            <span>
              <span className={`status-dot ${ecOk ? "" : "bad"}`} style={{ display: "inline-block", marginRight: 6 }} />
              EffectCraft v0.17.0 (MCP)
            </span>
            <span>
              <span className={`status-dot ${fcOk ? "" : "bad"}`} style={{ display: "inline-block", marginRight: 6 }} />
              FilmCraft v0.13.0 (MCP)
            </span>
          </div>
          <div style={{ marginTop: 8, paddingTop: 8, borderTop: "1px solid #1a2442" }}>
            <Link href="/settings?tab=effectcraft" style={{ color: "#60a5fa", fontSize: "0.76rem" }}>
              View MCP Connection Guide →
            </Link>
          </div>
        </div>
      </aside>

      <div className="app-body">
        <header className="top-bar">
          <div className="top-tagline">
            <span style={{ color: "var(--text)", fontWeight: 700 }}>From Script to Stunning Videos — Automatically</span>
          </div>

          <div className="status-strip" aria-label="Engine connections">
            <Link href="/settings?tab=providers" className="status-pill" title="AI Director (AWS Bedrock Claude Sonnet 4.5 & Haiku 4.5)">
              <span className={`status-dot ${awsOk ? "" : "warn"}`} />
              AI Director
            </Link>
            <Link href="/settings?tab=effectcraft" className="status-pill" title={health?.tools?.effectcraft?.detail ?? "EffectCraft MCP Server"}>
              <span className={`status-dot ${ecOk ? "" : "bad"}`} />
              EffectCraft (MCP)
            </Link>
            <Link href="/settings?tab=filmcraft" className="status-pill" title={health?.tools?.filmcraft?.detail ?? "FilmCraft MCP Server"}>
              <span className={`status-dot ${fcOk ? "" : "bad"}`} />
              FilmCraft (MCP)
            </Link>
            <Link href="/settings?tab=stock" className="status-pill" title={health?.stock?.detail ?? "Stock Media Asset Pipeline"}>
              <span className="status-dot" />
              Pexels / Pixabay
            </Link>
            <button
              type="button"
              className="secondary"
              style={{ padding: "4px 10px", fontSize: "0.76rem", borderRadius: 99 }}
              onClick={() => {
                const next = theme === "dark" ? "light" : "dark";
                setTheme(next);
                api.saveSettings({ theme: next }).catch(() => {});
              }}
              title="Switch Dark / Light Theme"
            >
              {theme === "dark" ? "☀ Light" : "☾ Dark"}
            </button>
            <button
              type="button"
              className="secondary"
              style={{ padding: "4px 10px", fontSize: "0.76rem", borderRadius: 99 }}
              onClick={() => {
                const next = accent === "blue" ? "purple" : "blue";
                setAccent(next);
                api.saveSettings({ accent_color: next }).catch(() => {});
              }}
              title="Switch Accent Palette (Blue Tech / Purple Creative)"
            >
              {accent === "blue" ? "◆ Blue" : "◆ Purple"}
            </button>
          </div>
        </header>

        <main className="workspace-content">{children}</main>

        <footer className="workflow-footer" aria-label="Complete workflow">
          <strong style={{ color: "var(--text)" }}>Complete Workflow:</strong>
          <div className="workflow-steps">
            {WORKFLOW_STEPS.map((st, i) => (
              <span key={st} className="wf-step">
                <span className="num">{i + 1}</span>
                {st}
              </span>
            ))}
          </div>
        </footer>
      </div>
    </div>
  );
}
