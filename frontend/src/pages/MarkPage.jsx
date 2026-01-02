import { useState } from "react";

export default function MarkPage() {
  const sessionId = localStorage.getItem("sessionId");

  const [studentName, setStudentName] = useState("");
  const [writingScore, setWritingScore] = useState("");
  const [readingFile, setReadingFile] = useState(null);
  const [qrArFile, setQrArFile] = useState(null);
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("");

    if (!sessionId) {
      setStatus("You must log in first.");
      return;
    }

    if (!studentName || !writingScore || !readingFile || !qrArFile) {
      setStatus("Please fill in all fields and upload both PDFs.");
      return;
    }

    try {
      setLoading(true);

      const formData = new FormData();
      formData.append("student_name", studentName);
      formData.append("writing_score", writingScore);
      formData.append("reading_pdf", readingFile);
      formData.append("qr_ar_pdf", qrArFile);

      const res = await fetch("http://localhost:8000/mark/single-student", {
        method: "POST",
        headers: {
          "X-Session-ID": sessionId,
        },
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text);
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = `${studentName}_marked_stub.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(url);

      setStatus("Download started.");
    } catch (err) {
      console.error(err);
      setStatus("Upload or download failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Mark ASET Sheet</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Student Name: </label>
          <input value={studentName} onChange={(e) => setStudentName(e.target.value)} />
        </div>

        <div>
          <label>Writing Score: </label>
          <input value={writingScore} onChange={(e) => setWritingScore(e.target.value)} />
        </div>

        <div>
          <label>Reading MCQ PDF: </label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setReadingFile(e.target.files[0] || null)}
          />
        </div>

        <div>
          <label>QR/AR MCQ PDF: </label>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setQrArFile(e.target.files[0] || null)}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Processing..." : "Generate ZIP (stub)"}
        </button>
      </form>

      {status && <p>{status}</p>}
    </div>
  );
}
