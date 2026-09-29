const API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '');

export async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const text = await response.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { detail: text }; }
  if (!response.ok) {
    throw new Error(data.detail || `API request failed (${response.status})`);
  }
  return data;
}

export async function uploadAndAnalyze(file, sampleRateHz = null, wideband = false) {
  const uploadBody = new FormData();
  uploadBody.append('file', file);
  const uploaded = await apiFetch('/upload', { method: 'POST', body: uploadBody });

  const analyzeBody = new FormData();
  analyzeBody.append('file_id', uploaded.file_id);
  analyzeBody.append('wideband', String(wideband));
  if (sampleRateHz) analyzeBody.append('sample_rate_hz', String(sampleRateHz));

  const analysis = await apiFetch('/analyze', { method: 'POST', body: analyzeBody });
  return { uploaded, analysis };
}

export { API_BASE };
