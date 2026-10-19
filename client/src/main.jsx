import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("React ErrorBoundary caught runtime exception:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: "2.5rem", background: "#09090b", color: "#f8fafc", height: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: "sans-serif", textAlign: "center" }}>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 800, color: "#f59e0b", marginBottom: "0.5rem" }}>NEXARCH Workspace Rendering Notice</h2>
          <p style={{ color: "#94a3b8", maxWidth: "500px", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
            {String(this.state.error?.message || this.state.error || "A component error occurred.")}
          </p>
          <button 
            onClick={() => window.location.reload()} 
            style={{ background: "#d4af37", color: "#18181b", padding: "0.6rem 1.25rem", border: "none", borderRadius: "8px", fontWeight: 800, cursor: "pointer" }}
          >
            Reload Workspace
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
