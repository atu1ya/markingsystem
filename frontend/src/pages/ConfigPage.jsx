import { useState } from "react";
import { apiRequest } from "../api";

export default function ConfigPage() {
  const sessionId = localStorage.getItem("sessionId");

  const [readingJson, setReadingJson] = useState("");
  const [qrArJson, setQrArJson] = useState("");
  const [conceptsJson, setConceptsJson] = useState("");
  const [message, setMessage] = useState("");

  async function uploadReading() {
    try {
      const parsed = JSON.parse(readingJson);
      await apiRequest("/config/reading-key", "POST", parsed, sessionId);
      setMessage("Reading key uploaded");
    } catch {
      setMessage("Invalid reading JSON");
    }
  }

  async function uploadQrAr() {
    try {
      const parsed = JSON.parse(qrArJson);
      await apiRequest("/config/qr-ar-key", "POST", parsed, sessionId);
      setMessage("QR/AR key uploaded");
    } catch {
      setMessage("Invalid QR/AR JSON");
    }
  }

  async function uploadConcepts() {
    try {
      const parsed = JSON.parse(conceptsJson);
      await apiRequest("/config/concepts", "POST", parsed, sessionId);
      setMessage("Concept map uploaded");
    } catch {
      setMessage("Invalid concept map JSON");
    }
  }

  function goNext() {
    window.location.href = "/mark";
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Admin Configuration</h1>

      <h2>Reading Answer Key JSON</h2>
      <textarea
        rows="6"
        cols="60"
        value={readingJson}
        onChange={(e) => setReadingJson(e.target.value)}
      />
      <button onClick={uploadReading}>Upload Reading Key</button>

      <h2>QR/AR Answer Key JSON</h2>
      <textarea
        rows="6"
        cols="60"
        value={qrArJson}
        onChange={(e) => setQrArJson(e.target.value)}
      />
      <button onClick={uploadQrAr}>Upload QR/AR Key</button>

      <h2>Concept Map JSON</h2>
      <textarea
        rows="6"
        cols="60"
        value={conceptsJson}
        onChange={(e) => setConceptsJson(e.target.value)}
      />
      <button onClick={uploadConcepts}>Upload Concept Map</button>

      {message && <p>{message}</p>}

      <hr />
      <button onClick={goNext}>Go to Marking Page</button>
    </div>
  );
}
