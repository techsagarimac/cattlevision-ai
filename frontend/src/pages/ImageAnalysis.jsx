import { useState } from "react";
import { Disclaimer, ErrorBox, RiskBadge } from "../components/Layout.jsx";
import { api, mediaUrl } from "../services/api.js";

export default function ImageAnalysis() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  function onFile(selected) {
    setFile(selected);
    setResult(null);
    setError("");
    if (selected) setPreview(URL.createObjectURL(selected));
  }

  async function run() {
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const payload = await api.analyzeImage(file);
      setResult(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>Image Analysis</h1>
          <p className="lede">Upload a cattle image. YOLO detects animals and a rule-based check estimates posture from the bounding box.</p>
        </div>
      </header>

      <div className="card dropzone">
        <p>Images: jpg, jpeg, png · max 10 MB</p>
        <input type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" onChange={(e) => onFile(e.target.files[0])} />
        <div className="row" style={{ justifyContent: "center", marginTop: 12 }}>
          <button className="btn btn-primary" disabled={!file || busy} onClick={run} type="button">
            {busy ? "Analyzing…" : "Run detection"}
          </button>
        </div>
      </div>

      <ErrorBox error={error} />

      <div className="preview-row">
        <div className="card">
          <h3>Original image</h3>
          {preview ? <img src={preview} alt="Original cattle upload" /> : <p className="muted">No image selected.</p>}
        </div>
        <div className="card">
          <h3>Processed image</h3>
          {result ? (
            <img src={mediaUrl(result.processed_image_url)} alt="Processed cattle detections" />
          ) : (
            <p className="muted">Results will appear here.</p>
          )}
        </div>
      </div>

      {result ? (
        <>
          <section className="grid grid-3">
            <article className="card">
              <p className="stat-label">Cattle detected</p>
              <p className="stat-value">{result.cattle_count}</p>
            </article>
            <article className="card">
              <p className="stat-label">Average confidence</p>
              <p className="stat-value">{Math.round(result.average_confidence * 100)}%</p>
            </article>
            <article className="card">
              <p className="stat-label">Model</p>
              <p className="stat-value" style={{ fontSize: "1.3rem" }}>{result.model_name}</p>
            </article>
          </section>
          <section className="card">
            <h3>Detections</h3>
            {result.detections.length === 0 ? (
              <p>No cattle detected. Try a clearer photo that includes cows.</p>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>Animal</th>
                    <th>Confidence</th>
                    <th>Position</th>
                    <th>Observation</th>
                    <th>Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {result.detections.map((det) => (
                    <tr key={det.animal_id}>
                      <td>{det.animal_id}</td>
                      <td>{Math.round(det.confidence * 100)}%</td>
                      <td>
                        x {Math.round(det.x)}, y {Math.round(det.y)}
                      </td>
                      <td>{det.behavior}</td>
                      <td>
                        <RiskBadge band={det.risk_band} score={det.risk_score} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
            <ul>
              {result.observations.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            <a className="btn btn-secondary" href={mediaUrl(result.processed_image_url)} download>
              Download processed image
            </a>
          </section>
          <Disclaimer text={result.disclaimer} />
        </>
      ) : null}
    </div>
  );
}
