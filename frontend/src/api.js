const BASE_URL = "http://localhost:8000";

export async function apiRequest(path, method = "GET", body = null, sessionId = null) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (sessionId) {
    headers["X-Session-ID"] = sessionId;
  }

  const options = { method, headers };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(BASE_URL + path, options);

  if (!response.ok) {
    const result = await response.text();
    throw new Error(result);
  }

  return await response.json();
}
