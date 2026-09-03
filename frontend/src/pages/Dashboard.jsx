import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ActivityChart, AlertsChart, BehaviorChart, RiskChart } from "../charts/Charts.jsx";
import { DemoBadge, Disclaimer, ErrorBox, RiskBadge, StatCard } from "../components/Layout.jsx";
import { api } from "../services/api.js";

export default function Dashboard() {
  const [includeDemo, setIncludeDemo] = useState(true);
  const [data, setData] = useState(null);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setError("");
    Promise.all([api.dashboard(includeDemo), api.health()])
      .then(([dash, hp]) => {
        if (!cancelled) {
          setData(dash);
          setHealth(hp);
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, [includeDemo]);

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>CattleVision AI</h1>
          <p className="lede">Computer Vision Based Cattle Monitoring</p>
        </div>
        <label className="toggle">
          <input type="checkbox" checked={includeDemo} onChange={(e) => setIncludeDemo(e.target.checked)} />
          Show demo data
        </label>
      </header>

      <div className="hero-actions">
        <Link to="/analyze/image">
          <strong>Analyze Image</strong>
          <span>Upload a cattle photo for YOLO detection.</span>
        </Link>
        <Link to="/analyze/video">
          <strong>Analyze Video</strong>
          <span>Track animals and estimate activity over time.</span>
        </Link>
        <Link to="/live">
          <strong>Live Camera</strong>
          <span>Optional webcam monitoring on this computer.</span>
        </Link>
      </div>

      {health && !health.model_loaded ? (
        <div className="notice warn">
          {health.model_message || "AI model not found. Please download/configure the model."} See models/README.md.
        </div>
      ) : null}

      <ErrorBox error={error} />

      {data ? (
        <>
          {data.includes_demo_data ? <DemoBadge /> : null}
          <section className="grid grid-4">
            <StatCard label="Total Cattle" value={data.total_animals} />
            <StatCard label="Current Alerts" value={data.current_alerts.length} />
            <StatCard label="Average Activity" value={`${data.average_activity}%`} />
            <StatCard label="Requiring Attention" value={data.animals_requiring_attention} />
          </section>
          <section className="grid grid-4">
            <StatCard label="Normal" value={data.normal} hint="Risk 0–30" />
            <StatCard label="Monitor" value={data.monitor} hint="Risk 31–60" />
            <StatCard label="Attention Required" value={data.attention_required} hint="Risk 61–80" />
            <StatCard label="Resting Animals" value={data.resting_animals} />
          </section>
          <div className="grid grid-2">
            <ActivityChart data={data.activity_over_time} />
            <BehaviorChart counts={data.behavior_counts} />
            <RiskChart distribution={data.risk_distribution} />
            <AlertsChart data={data.alerts_over_time} />
          </div>
          <section className="card">
            <h3>Current Alerts</h3>
            {data.current_alerts.length === 0 ? (
              <p className="muted">No open alerts.</p>
            ) : (
              <ul>
                {data.current_alerts.map((alert) => (
                  <li key={alert.id}>
                    ⚠ {alert.animal_identifier || "Unknown"} — {alert.alert_type}{" "}
                    <RiskBadge score={alert.risk_score} />
                    {alert.is_demo ? <DemoBadge /> : null}
                  </li>
                ))}
              </ul>
            )}
          </section>
          <Disclaimer text={data.disclaimer} />
        </>
      ) : null}
    </div>
  );
}
