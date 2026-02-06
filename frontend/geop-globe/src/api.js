const API_BASE = "http://127.0.0.1:8000/api";

export async function startProcessing({ mode, limit }) {
  const params = new URLSearchParams({ mode });
  if (limit) params.append("limit", limit);

  const res = await fetch(`${API_BASE}/process?${params.toString()}`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to start job");
  }

  return res.json();
}

export async function fetchJobStatus(jobName) {
  const res = await fetch(`${API_BASE}/jobs/${jobName}`);
  if (!res.ok) throw new Error("Failed to fetch job status");
  return res.json();
}

const API = "http://localhost:8000/api"

export async function runFullReboot() {
  return fetch(`${API}/reboot-full`, { method: "POST" })
}

export async function runIncrementalRefresh() {
  return fetch(`${API}/refresh-incremental`, { method: "POST" })
}

export async function runFetchPeriod(from, to) {
  return fetch(`${API}/fetch-period`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start_date: from, end_date: to })
  })
}

export async function runLLMProcessing(mode = "missing_states", limit = 500) {
  return fetch(`${API}/process?mode=${mode}&limit=${limit}`, {
    method: "POST"
  })
}

export async function resetLLMProcessing() {
  return fetch(`${API}/jobs/llm_processing/reset`, {
    method: "POST"
  })
}