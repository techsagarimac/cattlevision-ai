import { NavLink, Outlet } from "react-router-dom";
import { useState } from "react";

const LINKS = [
  ["/", "Dashboard"],
  ["/analyze/image", "Image Analysis"],
  ["/analyze/video", "Video Analysis"],
  ["/live", "Live Camera"],
  ["/animals", "Animals"],
  ["/alerts", "Alerts"],
  ["/history", "Analysis History"],
  ["/about", "About Project"],
];

export default function Layout() {
  const [open, setOpen] = useState(false);
  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">🐄</div>
          <h1 className="brand-title">CattleVision AI</h1>
          <p className="brand-sub">AI-Based Cattle Health & Welfare Monitoring</p>
        </div>
        <nav className="nav">
          {LINKS.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === "/"} onClick={() => setOpen(false)}>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          Educational computer-vision system. Not a veterinary diagnosis tool. Always inspect animals in person.
        </div>
      </aside>
      <main className="main">
        <button className="menu-btn" onClick={() => setOpen((v) => !v)} type="button">
          Menu
        </button>
        <Outlet />
      </main>
    </div>
  );
}

export function DemoBadge({ show = true }) {
  if (!show) return null;
  return <span className="badge badge-demo">DEMO DATA</span>;
}

export function RiskBadge({ band, score }) {
  const label = band || bandFromScore(score);
  const cls =
    label === "Normal"
      ? "badge-ok"
      : label === "Monitor"
        ? "badge-monitor"
        : "badge-attention";
  return (
    <span className={`badge ${cls}`}>
      {label}
      {score !== undefined && score !== null ? ` · ${Math.round(score)}` : ""}
    </span>
  );
}

export function bandFromScore(score = 0) {
  if (score <= 30) return "Normal";
  if (score <= 60) return "Monitor";
  if (score <= 80) return "Attention Required";
  return "High Attention";
}

export function Disclaimer({ text }) {
  return (
    <p className="notice">
      {text ||
        "CattleVision AI reports experimental visual indicators only. It cannot definitively diagnose disease. Veterinary inspection is recommended if concerns persist."}
    </p>
  );
}

export function ErrorBox({ error }) {
  if (!error) return null;
  return <div className="notice error">{error}</div>;
}

export function StatCard({ label, value, hint }) {
  return (
    <article className="card">
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
      {hint ? <p className="muted">{hint}</p> : null}
    </article>
  );
}
