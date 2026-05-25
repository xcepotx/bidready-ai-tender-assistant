export default function AuthPanel({
  authUser,
  authToken,
  authForm,
  setAuthForm,
  loginWithPassword,
  logoutUser,
  busy,
}) {
  return (
    <div className="authPanel">
      <div className="authPanelInfo">
        <span className={authUser ? "authStatus online" : "authStatus dev"}>
          {authUser ? "Authenticated" : "Dev Fallback"}
        </span>
        <div>
          <strong>{authUser?.full_name || authUser?.email || "Internal API Key Mode"}</strong>
          <p>{authUser ? `${authUser.email} · ${authUser.role}` : "Login is optional in dev; API key fallback is still enabled."}</p>
        </div>
      </div>

      {authUser ? (
        <button type="button" className="secondaryButton" onClick={logoutUser} disabled={busy}>
          Logout
        </button>
      ) : (
        <form className="authLoginForm" onSubmit={loginWithPassword}>
          <input
            type="email"
            placeholder="admin@bidready.local"
            value={authForm.email}
            onChange={(event) => setAuthForm((current) => ({ ...current, email: event.target.value }))}
            disabled={busy}
          />
          <input
            type="password"
            placeholder="Password"
            value={authForm.password}
            onChange={(event) => setAuthForm((current) => ({ ...current, password: event.target.value }))}
            disabled={busy}
          />
          <button type="submit" className="primaryButton" disabled={busy || !authForm.email || !authForm.password}>
            Login
          </button>
        </form>
      )}
    </div>
  );
}
