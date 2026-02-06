import { useState, useEffect } from "react"
import {
  runFullReboot,
  runIncrementalRefresh,
  runLLMProcessing,
  resetLLMProcessing,
  fetchJobStatus
} from "../api.js"

export default function Admin() {
  const [jobStatus, setJobStatus] = useState(null)

  useEffect(() => {
    const interval = setInterval(async () => {
      const status = await fetchJobStatus("llm_processing")
      setJobStatus(status)
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <div 
      style={{ 
        minHeight: "100vh",
        background: "linear-gradient(135deg, #000000ff 0%, #0e2777ff 100%)",
        color: "white",
        padding: "48px 24px",
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
      }}
    >
      <div style={{ maxWidth: "800px", margin: "0 auto" }}>
        <h2 style={{ fontSize: "2rem", fontWeight: "400", marginBottom: "32px" }}>
          Backend Control Panel
        </h2>

        <section style={{ marginBottom: "32px" }}>
          <h3 style={{ fontSize: "1.25rem", fontWeight: "400", marginBottom: "16px" }}>
            Data Ingestion
          </h3>
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <button 
              onClick={runFullReboot}
              style={{
                padding: "12px 24px",
                fontSize: "1rem",
                fontWeight: "400",
                color: "white",
                background: "#1e40af",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                borderRadius: "4px",
                cursor: "pointer",
                transition: "background 0.2s ease",
                fontFamily: "inherit"
              }}
              onMouseEnter={(e) => e.target.style.background = "#1e3a8a"}
              onMouseLeave={(e) => e.target.style.background = "#1e40af"}
            >
              Full Reboot (Last 3 Months)
            </button>

            <button 
              onClick={runIncrementalRefresh}
              style={{
                padding: "12px 24px",
                fontSize: "1rem",
                fontWeight: "400",
                color: "white",
                background: "#1e40af",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                borderRadius: "4px",
                cursor: "pointer",
                transition: "background 0.2s ease",
                fontFamily: "inherit"
              }}
              onMouseEnter={(e) => e.target.style.background = "#1e3a8a"}
              onMouseLeave={(e) => e.target.style.background = "#1e40af"}
            >
              Incremental Refresh
            </button>
          </div>
        </section>

        <section style={{ marginBottom: "32px" }}>
          <h3 style={{ fontSize: "1.25rem", fontWeight: "400", marginBottom: "16px" }}>
            LLM Processing
          </h3>
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <button 
              onClick={() => runLLMProcessing()}
              style={{
                padding: "12px 24px",
                fontSize: "1rem",
                fontWeight: "400",
                color: "white",
                background: "#1e40af",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                borderRadius: "4px",
                cursor: "pointer",
                transition: "background 0.2s ease",
                fontFamily: "inherit"
              }}
              onMouseEnter={(e) => e.target.style.background = "#1e3a8a"}
              onMouseLeave={(e) => e.target.style.background = "#1e40af"}
            >
              Run LLM Processing
            </button>

            <button 
              onClick={resetLLMProcessing}
              style={{
                padding: "12px 24px",
                fontSize: "1rem",
                fontWeight: "400",
                color: "white",
                background: "#dc2626",
                border: "1px solid rgba(255, 255, 255, 0.2)",
                borderRadius: "4px",
                cursor: "pointer",
                transition: "background 0.2s ease",
                fontFamily: "inherit"
              }}
              onMouseEnter={(e) => e.target.style.background = "#b91c1c"}
              onMouseLeave={(e) => e.target.style.background = "#dc2626"}
            >
              Kill LLM Process
            </button>
          </div>
        </section>

        <section>
          <h3 style={{ fontSize: "1.25rem", fontWeight: "400", marginBottom: "16px" }}>
            Status
          </h3>
          <pre 
            style={{ 
              background: "rgba(0, 0, 0, 0.3)", 
              padding: "16px", 
              borderRadius: "4px",
              border: "1px solid rgba(255, 255, 255, 0.1)",
              overflow: "auto",
              fontSize: "0.875rem"
            }}
          >
            {JSON.stringify(jobStatus, null, 2)}
          </pre>
        </section>
      </div>
    </div>
  )
}
