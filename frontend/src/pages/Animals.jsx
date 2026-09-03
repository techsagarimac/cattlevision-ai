import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { DemoBadge, ErrorBox, RiskBadge } from "../components/Layout.jsx";
import { api } from "../services/api.js";

export default function Animals() {
  const [includeDemo, setIncludeDemo] = useState(true);
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setRows(null);
    api.animals(includeDemo).then(setRows).catch((err) => setError(err.message));
  }, [includeDemo]);

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>Animals</h1>
          <p className="lede">Tracked cattle from demo records and your analysis sessions.</p>
        </div>
        <label className="toggle">
          <input type="checkbox" checked={includeDemo} onChange={(e) => setIncludeDemo(e.target.checked)} />
          Show demo data
        </label>
      </header>
      <ErrorBox error={error} />
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Animal</th>
              <th>Behavior</th>
              <th>Risk</th>
              <th>Confidence</th>
              <th>Alerts</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows?.map((animal) => (
              <tr key={animal.id}>
                <td>
                  {animal.animal_identifier} {animal.is_demo ? <DemoBadge /> : null}
                </td>
                <td>{animal.last_behavior || "—"}</td>
                <td>
                  <RiskBadge score={animal.last_risk_score} />
                </td>
                <td>{Math.round((animal.last_confidence || 0) * 100)}%</td>
                <td>{animal.open_alerts}</td>
                <td>
                  <Link to={`/animals/${animal.id}`}>Details</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows === null ? <p className="muted">Loading…</p> : null}
        {rows && rows.length === 0 ? <p className="muted">No animals yet. Analyze an image/video or keep demo data enabled.</p> : null}
      </div>
    </div>
  );
}
