const API = "/api";

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API}${path}`, options);
  } catch (error) {
    throw new Error("Cannot reach the CattleVision AI backend. Start the FastAPI server on port 8000.");
  }
  const isJson = (response.headers.get("content-type") || "").includes("application/json");
  const body = isJson ? await response.json() : null;
  if (!response.ok) {
    const message = body?.message || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return body;
}

export const api = {
  health: () => request("/health"),
  modelStatus: () => request("/model/status"),
  dashboard: (includeDemo = true) => request(`/dashboard?include_demo=${includeDemo}`),
  animals: (includeDemo = true) => request(`/animals?include_demo=${includeDemo}`),
  animal: (id) => request(`/animals/${id}`),
  alerts: (includeDemo = true, resolved) => {
    const params = new URLSearchParams({ include_demo: includeDemo });
    if (resolved !== undefined && resolved !== "") params.set("resolved", resolved);
    return request(`/alerts?${params}`);
  },
  resolveAlert: (id) => request(`/alerts/${id}/resolve`, { method: "POST" }),
  analysisList: () => request("/analysis"),
  analysis: (id) => request(`/analysis/${id}`),
  analyzeImage: (file) => {
    const data = new FormData();
    data.append("file", file);
    return request("/analyze/image", { method: "POST", body: data });
  },
  analyzeVideo: (file) => {
    const data = new FormData();
    data.append("file", file);
    return request("/analyze/video", { method: "POST", body: data });
  },
  videoJob: (jobId) => request(`/analyze/video/${jobId}`),
  analyzeFrame: (blob, sessionToken) => {
    const data = new FormData();
    data.append("file", blob, "frame.jpg");
    data.append("session_token", sessionToken);
    return request("/analyze/frame", { method: "POST", body: data });
  },
  resetLive: (sessionToken) =>
    request(`/analyze/frame/reset?session_token=${encodeURIComponent(sessionToken)}`, { method: "POST" }),
};

export function mediaUrl(path) {
  if (!path) return "";
  return path.startsWith("http") ? path : path;
}
