import { useEffect, useState } from "react";
import { DemoBadge, ErrorBox } from "../components/Layout.jsx";
import { api, mediaUrl } from "../services/api.js";

export default function AnalysisHistory() {
  const [rows, setRows] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.analysisList().then(setRows).catch((err) => setError(err.message));
  }, []);

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>Analysis History</h1>
          <p className="lede">Image, video, live, and demo sessions stored in SQLite.</p>
        </div>
      </header>
      <ErrorBox error={error} />
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>File / name</th>
              <th>Type</th>
              <th>Animals</th>
              <th>Alerts</th>
              <th>Status</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td>
                  {row.file_name} {row.is_demo ? <DemoBadge /> : null}
                </td>
                <td>{row.analysis_type}</td>
                <td>{row.total_animals}</td>
                <td>{row.total_alerts}</td>
                <td>{row.status}</td>
                <td>
                  {row.processed_url ? (
                    <a href={mediaUrl(row.processed_url)} target="_blank" rel="noreferrer">
                      Open
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
