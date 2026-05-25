export function getStoredAuthToken() {
  return window.localStorage.getItem("bidreadyAuthToken");
}

export function getStoredAuthUser() {
  try {
    const raw = window.localStorage.getItem("bidreadyAuthUser");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function buildAuthHeaders(extraHeaders = {}) {
  const token = getStoredAuthToken();
  const headers = { ...extraHeaders };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  } else {
    headers["X-Internal-API-Key"] = INTERNAL_API_KEY;
  }

  return headers;
}
