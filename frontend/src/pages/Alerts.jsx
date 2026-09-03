import { useEffect, useState } from "react";
import { DemoBadge, ErrorBox, RiskBadge } from "../components/Layout.jsx";
import { api } from "../services/api.js";

export default function Alerts() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");
  const [includeDemo, setIncludeDemo] = useState(true);

  function load() {
    api.alerts(includeDemo).then(setRows).catch((err) => setError(err.message));
  }

  useEffect(() => {
    load();
  }, [includeDemo]);

  async function resolve(id) {
    try {
      await api.resolveAlert(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>Alerts</h1>
          <p className="lede">Early-warning visual flags. These are not diagnoses.</p>
        </div>
        <label className="toggle">
          <input type="checkbox" checked={includeDemo} onChange={(e) => setIncludeDemo(e.target.checked)} />
          Show demo data
        </label>
      </header>
      <ErrorBox error={error} />
      {(rows || []).map((alert) => (
        <article className="card" key={alert.id}>
          <div className="row">
            <strong>⚠ ALERT</strong>
            <RiskBadge score={alert.risk_score} />
            {alert.is_demo ? <DemoBadge /> : null}
            {alert.resolved ? <span className="badge badge-ok">Resolved</span> : null}
          </div>
          <p>Animal: {alert.animal_identifier || "Unknown"}</p>
          <p>Issue: {alert.alert_type}</p>
          <p>Risk score: {Math.round(alert.risk_score)}</p>
          <p>Time: {new Date(alert.timestamp).toLocaleString()}</p>
          <p>{alert.message}</p>
          <p>{alert.recommendation}</p>
          {!alert.resolved ? (
            <button className="btn btn-secondary" type="button" onClick={() => resolve(alert.id)}>
              Mark resolved
            </button>
          ) : null}
        </article>
      ))}
      {rows === null ? <p className="muted">Loading…</p> : null}
      {rows && rows.length === 0 ? <p className="muted">No alerts.</p> : null}
    </div>
  );
}
