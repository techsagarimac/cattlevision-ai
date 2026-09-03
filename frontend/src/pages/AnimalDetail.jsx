import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { DemoBadge, Disclaimer, ErrorBox, RiskBadge, StatCard } from "../components/Layout.jsx";
import { api } from "../services/api.js";

export default function AnimalDetail() {
  const { animalId } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.animal(animalId).then(setData).catch((err) => setError(err.message));
  }, [animalId]);

  if (error) return <ErrorBox error={error} />;
  if (!data) return <p>Loading…</p>;

  const minutes = Math.round((data.time_monitored_seconds || 0) / 60);

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>{data.animal_identifier.toUpperCase()}</h1>
          <p className="lede">Current status and experimental visual history for this animal record.</p>
        </div>
        {data.is_demo ? <DemoBadge /> : null}
      </header>
      <section className="grid grid-4">
        <StatCard label="Current behavior" value={data.current_behavior || "—"} />
        <article className="card">
          <p className="stat-label">Current status</p>
          <RiskBadge score={data.risk_score} />
        </article>
        <StatCard label="Risk score" value={`${Math.round(data.risk_score)} / 100`} />
        <StatCard label="Monitoring duration" value={`${minutes} min`} />
      </section>
      <section className="grid grid-2">
        <article className="card">
          <p className="stat-label">Activity score</p>
          <p className="stat-value">{data.activity_score}</p>
        </article>
        <article className="card">
          <p className="stat-label">Detection confidence</p>
          <p className="stat-value">{Math.round(data.detection_confidence * 100)}%</p>
        </article>
      </section>
      <section className="card">
        <h3>Recent activity</h3>
        <ul>
          {data.observations.slice(0, 12).map((obs) => (
            <li key={obs.id}>
              {new Date(obs.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} — {obs.behavior}
            </li>
          ))}
        </ul>
      </section>
      <section className="card">
        <h3>Behavior history</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Activity</th>
              <th>Duration</th>
              <th>Movement</th>
            </tr>
          </thead>
          <tbody>
            {data.behavior_history.map((row) => (
              <tr key={row.id}>
                <td>{row.behavior}</td>
                <td>{Math.round(row.duration_seconds / 60) || "<1"} min</td>
                <td>{row.movement_label}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="card">
        <h3>Alerts</h3>
        {data.alerts.length === 0 ? <p className="muted">No alerts for this animal.</p> : null}
        {data.alerts.map((alert) => (
          <p key={alert.id}>
            {alert.message.startsWith("⚠") ? alert.message : `⚠ ${alert.message}`} <RiskBadge score={alert.risk_score} />
          </p>
        ))}
      </section>
      <section className="card">
        <h3>Recommendation</h3>
        <p>{data.recommendation}</p>
      </section>
      <Disclaimer text={data.disclaimer} />
    </div>
  );
}
