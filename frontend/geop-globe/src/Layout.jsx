import { Link, Outlet } from "react-router-dom"

export default function Layout() {
  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          height: 48,
          display: "flex",
          gap: 12,
          alignItems: "center",
          padding: "0 12px",
          background: "rgba(0,0,0,0.6)",
          color: "white",
          zIndex: 10
        }}
      >
        <Link to="/" style={{ color: "white" }}>Home</Link>
        <Link to="/map" style={{ color: "white" }}>Map</Link>
        <Link to="/admin" style={{ color: "white" }}>Admin</Link>
      </div>

      <div style={{ paddingTop: 48, width: "100%", height: "100%" }}>
        <Outlet />
      </div>
    </div>
  )
}
