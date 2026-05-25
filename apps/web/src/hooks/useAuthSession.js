import { useState } from "react";
import { apiFetch } from "../api/client.js";
import { getStoredAuthToken, getStoredAuthUser } from "../utils/auth.js";

const defaultAuthForm = {
  email: "admin@bidready.local",
  password: "",
};

export function useAuthSession({ setBusy, setMessage, setActorName } = {}) {
  const [authUser, setAuthUser] = useState(() => getStoredAuthUser());
  const [authToken, setAuthToken] = useState(() => getStoredAuthToken());
  const [authForm, setAuthForm] = useState(defaultAuthForm);

  async function loginWithPassword(event) {
    event.preventDefault();
    setBusy?.(true);
    setMessage?.("Signing in...");

    try {
      const result = await apiFetch("/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(authForm),
      });

      window.localStorage.setItem("bidreadyAuthToken", result.access_token);
      window.localStorage.setItem("bidreadyAuthUser", JSON.stringify(result.user));
      setAuthToken(result.access_token);
      setAuthUser(result.user);
      setActorName?.(result.user?.email || "authenticated_user");
      setMessage?.(`Signed in as ${result.user?.email || "user"}.`);
    } catch (err) {
      setMessage?.(`Login failed: ${err.message}`);
    } finally {
      setBusy?.(false);
    }
  }

  function logoutUser() {
    window.localStorage.removeItem("bidreadyAuthToken");
    window.localStorage.removeItem("bidreadyAuthUser");
    setAuthToken(null);
    setAuthUser(null);
    setMessage?.("Signed out. Dev fallback internal API key remains available.");
  }

  return {
    authUser,
    authToken,
    authForm,
    setAuthForm,
    loginWithPassword,
    logoutUser,
  };
}
