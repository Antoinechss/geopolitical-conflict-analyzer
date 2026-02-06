import { Link } from "react-router-dom"

export default function Home() {
  return (
    <div 
      style={{ 
        position: "relative",
        width: "100vw",
        height: "100vh",
        backgroundImage: "url(/homepage.png)",
        backgroundSize: "cover",
        backgroundPosition: "center",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        color: "white",
        textAlign: "center"
      }}
    >
      {/* Overlay for better text readability */}
      <div 
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          zIndex: 1
        }}
      />

      {/* Content */}
      <div style={{ position: "relative", zIndex: 2, padding: "0 20px" }}>
        <h1 
          style={{ 
            fontSize: "3rem",
            fontWeight: "400",
            marginBottom: "3rem",
            textShadow: "2px 2px 8px rgba(0, 0, 0, 0.8)",
            fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
          }}
        >
          Actor-Target Geopolitics Analyzer
        </h1>

        <div style={{ display: "flex", gap: "16px", justifyContent: "center", flexWrap: "wrap" }}>
          <Link 
            to="/map"
            style={{
              padding: "12px 32px",
              fontSize: "1rem",
              fontWeight: "400",
              color: "white",
              background: "#1e40af",
              border: "none",
              borderRadius: "4px",
              textDecoration: "none",
              transition: "background 0.2s ease",
              cursor: "pointer",
              fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "#1e3a8a"
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "#1e40af"
            }}
          >
            Map
          </Link>

          <Link 
            to="/admin"
            style={{
              padding: "12px 32px",
              fontSize: "1rem",
              fontWeight: "400",
              color: "white",
              background: "#1e40af",
              border: "none",
              borderRadius: "4px",
              textDecoration: "none",
              transition: "background 0.2s ease",
              cursor: "pointer",
              fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
            }}
            onMouseEnter={(e) => {
              e.target.style.background = "#1e3a8a"
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "#1e40af"
            }}
          >
            Admin
          </Link>
        </div>
      </div>
    </div>
  )
}
