import { buildAuthHeaders } from "../utils/auth.js";

export const API_BASE = import.meta.env.VITE_API_BASE || "/api/v1";

export function buildApiUrl(path) {
  if (!path) return API_BASE;
  if (/^https?:\/\//i.test(path)) return path;
  if (path.startsWith("/api/")) return path;
  if (path.startsWith("/")) return `${API_BASE}${path}`;
  return `${API_BASE}/${path}`;
}

export async function apiRequest(path, options = {}) {
  const {
    headers,
    body,
    json,
    responseType = "json",
    ...rest
  } = options;

  const finalHeaders = buildAuthHeaders(headers || {});

  let finalBody = body;

  if (json !== undefined) {
    finalHeaders["Content-Type"] = finalHeaders["Content-Type"] || "application/json";
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

export async function apiDownload(path, filename) {
  const blob = await apiRequest(path, {
    method: "GET",
    responseType: "blob",
  });

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

export async function apiUpload(path, formData, options = {}) {
  return apiRequest(path, {
    ...options,
    method: options.method || "POST",
    body: formData,
  });
}
