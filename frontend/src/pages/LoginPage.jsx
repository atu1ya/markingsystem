import { useState } from "react";
import { apiRequest } from "../api";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleLogin() {
    try {
      const res = await apiRequest("/auth/login", "POST", { password });
      localStorage.setItem("sessionId", res.session_id);
      window.location.href = "/config";
    } catch (err) {
      setError("Incorrect password");
    }
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Login</h1>
      <input
        type="password"
        placeholder="Enter admin password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={handleLogin}>Login</button>

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
