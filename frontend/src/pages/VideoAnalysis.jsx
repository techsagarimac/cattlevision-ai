import { useState } from "react";
import { Disclaimer, ErrorBox } from "../components/Layout.jsx";
import { api, mediaUrl } from "../services/api.js";

export default function VideoAnalysis() {
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [job, setJob] = useState(null);

  async function start() {
    if (!file) return;
    setBusy(true);
    setError("");
    setJob({ status: "queued", progress: 0, message: "Uploading video…" });
    try {
      const started = await api.analyzeVideo(file);
      poll(started.job_id);
    } catch (err) {
      setBusy(false);
      setError(err.message);
    }
  }

  function poll(jobId) {
    const timer = setInterval(async () => {
      try {
        const status = await api.videoJob(jobId);
        setJob(status);
        if (status.status === "completed" || status.status === "failed") {
          clearInterval(timer);
          setBusy(false);
        }
      } catch (err) {
        clearInterval(timer);
        setBusy(false);
        setError(err.message);
      }
    }, 1000);
  }

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>Video Analysis</h1>
          <p className="lede">
            Processing runs on the backend so the browser stays responsive. Tracking IDs are approximate and can switch
            under occlusion.
          </p>
        </div>
      </header>

      <div className="card dropzone">
        <p>Videos: mp4, avi, mov · max 80 MB</p>
        <input type="file" accept=".mp4,.avi,.mov,video/mp4,video/quicktime" onChange={(e) => setFile(e.target.files[0])} />
        <div className="row" style={{ justifyContent: "center", marginTop: 12 }}>
          <button className="btn btn-primary" disabled={!file || busy} onClick={start} type="button">
            {busy ? "Processing…" : "Analyze video"}
          </button>
        </div>
      </div>

      <ErrorBox error={error} />

      {job ? (
        <section className="card">
          <h3>Progress</h3>
          <p>{job.message}</p>
          <div className="progress">
            <div style={{ width: `${job.progress || 0}%` }} />
          </div>
          <p className="muted">{Math.round(job.progress || 0)}% · {job.status}</p>
          {job.error ? <p className="notice error">{job.error}</p> : null}
        </section>
      ) : null}

      {job?.status === "completed" ? (
        <>
          <section className="grid grid-3">
            <article className="card">
              <p className="stat-label">Total cattle tracked</p>
              <p className="stat-value">{job.cattle_count}</p>
            </article>
            <article className="card">
              <p className="stat-label">Average activity</p>
              <p className="stat-value">{job.average_activity}</p>
            </article>
            <article className="card">
              <p className="stat-label">Alerts generated</p>
              <p className="stat-value">{job.alerts_generated}</p>
            </article>
          </section>
          <section className="card">
            <h3>Behavior statistics</h3>
            <ul>
              {Object.entries(job.behavior_stats || {}).map(([name, value]) => (
                <li key={name}>
                  {name}: {value} frame observations
                </li>
              ))}
            </ul>
            {job.processed_video_url ? (
              <>
                <video src={mediaUrl(job.processed_video_url)} controls />
                <p>
                  <a className="btn btn-secondary" href={mediaUrl(job.processed_video_url)} download>
                    Download processed video
                  </a>
                </p>
              </>
            ) : (
              <p className="muted">Processed video file was not written (codec unavailable), but metrics were saved.</p>
            )}
          </section>
          <Disclaimer text={job.disclaimer} />
        </>
      ) : null}
    </div>
  );
}
