import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import LoginPage from "./pages/LoginPage.jsx";
import ConfigPage from "./pages/ConfigPage.jsx";
import MarkPage from "./pages/MarkPage.jsx";
import "./index.css";

function AppRouter() {
  return (
    <BrowserRouter>
      <nav style={{ padding: "1rem", borderBottom: "1px solid #ccc" }}>
        <Link to="/login" style={{ marginRight: "1rem" }}>
          Login
        </Link>
        <Link to="/config" style={{ marginRight: "1rem" }}>
          Config
        </Link>
        <Link to="/mark">Mark</Link>
      </nav>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/config" element={<ConfigPage />} />
        <Route path="/mark" element={<MarkPage />} />
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AppRouter />
  </React.StrictMode>
);
