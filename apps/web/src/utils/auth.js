const AUTH_TOKEN_STORAGE_KEY = "bidreadyAuthToken";
const AUTH_USER_STORAGE_KEY = "bidreadyAuthUser";

export function getStoredAuthToken() {
  return window.localStorage.getItem(AUTH_TOKEN_STORAGE_KEY);
}

export function getStoredAuthUser() {
  const raw = window.localStorage.getItem(AUTH_USER_STORAGE_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    window.localStorage.removeItem(AUTH_USER_STORAGE_KEY);
    return null;
  }
}

export function buildAuthHeaders(extraHeaders = {}) {
  const headers = {
    ...extraHeaders,
  };

  const token = getStoredAuthToken();

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}
