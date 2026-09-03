import { useEffect, useRef, useState } from "react";
import { Disclaimer, ErrorBox, RiskBadge } from "../components/Layout.jsx";
import { api } from "../services/api.js";

const TOKEN = "browser-webcam";

export default function LiveCamera() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const overlayRef = useRef(null);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [modelMessage, setModelMessage] = useState("");

  useEffect(() => {
    api.health().then((h) => {
      if (!h.model_loaded) setModelMessage(h.model_message || "AI model not found. Please download/configure the model.");
    }).catch((err) => setError(err.message));
  }, []);

  async function start() {
    setError("");
    if (!navigator.mediaDevices?.getUserMedia) {
      setError("This browser does not support webcam access. Use image or video upload instead.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
      await api.resetLive(TOKEN);
      setRunning(true);
    } catch (err) {
      setError("Webcam unavailable or permission denied. CattleVision AI still works with uploaded images and videos.");
    }
  }

  function stop() {
    setRunning(false);
    const stream = videoRef.current?.srcObject;
    if (stream) stream.getTracks().forEach((track) => track.stop());
  }

  useEffect(() => {
    if (!running) return undefined;
    const timer = setInterval(capture, 700);
    return () => clearInterval(timer);
  }, [running]);

  async function capture() {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.7));
    if (!blob) return;
    try {
      const payload = await api.analyzeFrame(blob, TOKEN);
      setResult(payload);
      drawOverlay(payload.detections, canvas.width, canvas.height);
    } catch (err) {
      setError(err.message);
      setRunning(false);
    }
  }

  function drawOverlay(detections, w, h) {
    const overlay = overlayRef.current;
    const video = videoRef.current;
    if (!overlay || !video) return;
    overlay.width = video.clientWidth;
    overlay.height = video.clientHeight;
    const ctx = overlay.getContext("2d");
    ctx.clearRect(0, 0, overlay.width, overlay.height);
    const sx = overlay.width / w;
    const sy = overlay.height / h;
    (detections || []).forEach((det) => {
      ctx.strokeStyle = det.risk_score > 60 ? "#c0392b" : det.risk_score > 30 ? "#d68910" : "#27ae60";
      ctx.lineWidth = 3;
      ctx.strokeRect(det.x * sx, det.y * sy, det.width * sx, det.height * sy);
      ctx.fillStyle = ctx.strokeStyle;
      ctx.font = "14px Source Sans 3, sans-serif";
      ctx.fillText(`${det.animal_id} ${Math.round(det.confidence * 100)}% ${det.behavior}`, det.x * sx, Math.max(14, det.y * sy - 6));
    });
  }

  useEffect(() => () => stop(), []);

  return (
    <div className="stack">
      <header className="page-head">
        <div>
          <h1>Live Camera</h1>
          <p className="lede">Optional webcam view. If no camera is available, use Image Analysis or Video Analysis instead.</p>
        </div>
        <div className="actions">
          {running ? (
            <button className="btn btn-danger" onClick={stop} type="button">Stop</button>
          ) : (
            <button className="btn btn-primary" onClick={start} type="button">Start camera</button>
          )}
        </div>
      </header>

      {modelMessage ? <div className="notice warn">{modelMessage}</div> : null}
      <ErrorBox error={error} />

      <div className="live-wrap">
        <video ref={videoRef} playsInline muted />
        <canvas ref={overlayRef} />
      </div>
      <canvas ref={canvasRef} hidden />

      <section className="card">
        <h3>LIVE CAMERA</h3>
        <p>Detected cattle: {result?.cattle_count ?? 0}</p>
        {(result?.detections || []).map((det) => (
          <p key={det.animal_id}>
            {det.animal_id} — {det.behavior} <RiskBadge band={det.risk_band} score={det.risk_score} />
          </p>
        ))}
        {(result?.alerts || []).map((line) => (
          <p key={line}>⚠ {line}</p>
        ))}
        {!result ? <p className="muted">Start the camera to see detections.</p> : null}
      </section>
      <Disclaimer text={result?.disclaimer} />
    </div>
  );
}
