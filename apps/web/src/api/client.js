import { buildAuthHeaders } from "../utils/auth.js";

export const API_BASE = import.meta.env.VITE_API_BASE || "/api/v1";

function shouldAttachInternalApiKey(path) {
  return typeof path === "string" && path.startsWith("/api/v1/");
}

function buildHeaders(path, inputHeaders = {}) {
  const internalApiKey = import.meta.env.VITE_INTERNAL_API_KEY || "";
  const headers = new Headers(buildAuthHeaders(inputHeaders || {}));

  if (shouldAttachInternalApiKey(path) && internalApiKey) {
    headers.set("X-Internal-API-Key", internalApiKey);
  }

  return headers;
}

export function buildApiUrl(path) {
  if (!path) return API_BASE;
  if (/^https?:\/\//i.test(path)) return path;
  if (path.startsWith("/api/")) return path;
  if (path.startsWith("/")) return `${API_BASE}${path}`;
  return `${API_BASE}/${path}`;
}

export async function apiFetch(path, options = {}) {
  const headers = buildHeaders(path, options.headers || {});

  const res = await fetch(buildApiUrl(path), {
    ...options,
    headers,
  });

  const text = await res.text();

  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!res.ok) {
    const detail = data?.detail || data || `HTTP ${res.status}`;
    throw new Error(detail);
  }

  return data;
}

export async function apiRequest(path, options = {}) {
  const {
    headers,
    body,
    json,
    responseType = "json",
    ...rest
  } = options;

  const finalHeaders = buildHeaders(path, headers || {});
  let finalBody = body;

  if (json !== undefined) {
    finalHeaders.set("Content-Type", finalHeaders.get("Content-Type") || "application/json");
    finalBody = JSON.stringify(json);
  }

  const response = await fetch(buildApiUrl(path), {
    ...rest,
    headers: finalHeaders,
    body: finalBody,
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;

    try {
      const payload = await response.json();
      detail = payload?.detail || payload?.message || detail;
    } catch {
      try {
        const text = await response.text();
        if (text) detail = text;
      } catch {
        // keep default detail
      }
    }

    const error = new Error(detail);
    error.status = response.status;
    error.response = response;
    throw error;
  }

  if (responseType === "response") return response;
  if (response.status === 204) return null;
  if (responseType === "blob") return response.blob();
  if (responseType === "text") return response.text();

  return response.json();
}

export function apiGet(path, options = {}) {
  return apiRequest(path, {
    ...options,
    method: "GET",
  });
}

export function apiPost(path, json, options = {}) {
  return apiRequest(path, {
    ...options,
    method: "POST",
    json,
  });
}

export function apiPatch(path, json, options = {}) {
  return apiRequest(path, {
    ...options,
    method: "PATCH",
    json,
  });
}

export function apiDelete(path, options = {}) {
  return apiRequest(path, {
    ...options,
    method: "DELETE",
  });
}

export async function downloadApiFile(path, filename) {
  const response = await fetch(buildApiUrl(path), {
    headers: buildHeaders(path),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Download failed with status ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename || "download";
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);

  return true;
}

export const apiDownload = downloadApiFile;

export async function apiUpload(path, formData, options = {}) {
  return apiRequest(path, {
    ...options,
    method: options.method || "POST",
    body: formData,
  });
}
