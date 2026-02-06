import { useEffect, useState, useMemo } from "react"
import DeckGL from "@deck.gl/react"
import { _GlobeView as GlobeView } from "@deck.gl/core"
import { TileLayer } from "@deck.gl/geo-layers"
import { BitmapLayer, ScatterplotLayer, ArcLayer } from "@deck.gl/layers"




// Helper functions 

function eventColor(type, alpha = 140) {
  switch (type) {
    case "ATTACK": return [220, 60, 60, alpha]
    case "THREAT": return [255, 140, 0, alpha]
    case "DIPLOMATIC_ACTION": return [60, 160, 255, alpha]
    case "COERCIVE_ACTION": return [200, 80, 255, alpha]
    case "PROTEST": return [108, 113, 196, alpha]
    case "CYBER_OPERATION": return [42, 161, 152, alpha]
    case "TERRORISM": return [133, 153, 0, alpha]
    case "UNDEFINED": return [160, 160, 160, alpha]
    default: return [180, 180, 180, alpha]
  }
}

function computeFromDate(range) {
  if (range === "ALL") return null

  const now = new Date()
  const days =
    range === "7D" ? 7 :
    range === "30D" ? 30 :
    range === "90D" ? 90 :
    null

  if (!days) return null

  const d = new Date(now)
  d.setDate(d.getDate() - days)
  return d.toISOString().slice(0, 10)
}

function eventOffset(eventType) {
  let h = 0
  for (let i = 0; i < eventType.length; i++) {
    h = (h * 31 + eventType.charCodeAt(i)) % 1000
  }
  return (h - 500) / 200 * Math.sign(Math.sin(h))
 // small angular offset
}



// ----- Main visualization --------- 

export default function Map() {
  const [states, setStates] = useState([])
  const [relations, setRelations] = useState([])
  const [hoverInfo, setHoverInfo] = useState(null)
  const [timeRange, setTimeRange] = useState("30D")
  const [time, setTime] = useState(0)
  const [selectedEventTypes, setSelectedEventTypes] = useState(new Set())

  const EVENT_COLORS = {
    ATTACK: [220, 50, 47, 255],
    THREAT: [203, 75, 22, 255],
    COERCIVE_ACTION: [181, 137, 0, 255],
    DIPLOMATIC_ACTION: [38, 139, 210, 255],
    PROTEST: [108, 113, 196, 255],
    CYBER_OPERATION: [42, 161, 152, 255],
    TERRORISM: [133, 153, 0, 255],
    UNDEFINED: [160, 160, 160, 255]
  }
  const DEFAULT_COLOR = [180, 180, 180, 255]

  // Toggle event type selection
  const toggleEventType = (type) => {
    setSelectedEventTypes(prev => {
      const newSet = new Set(prev)
      if (newSet.has(type)) {
        newSet.delete(type)
      } else {
        newSet.add(type)
      }
      return newSet
    })
  }

  // Animation ticker
  useEffect(() => {
    let frame
    const animate = () => {
      setTime(t => t + 0.05)
      frame = requestAnimationFrame(animate)
    }
    animate()
    return () => cancelAnimationFrame(frame)
  }, [])

  // Load states
  useEffect(() => {
    fetch("/states.deck.json")
      .then(r => r.json())
      .then(setStates)
      .catch(console.error)
  }, [])

  // Load relations (time-filtered)
  useEffect(() => {
    const from = computeFromDate(timeRange)

    const url = from
      ? `http://localhost:8000/api/relations?from=${from}`
      : `http://localhost:8000/api/relations`

    fetch(url)
      .then(r => r.json())
      .then(data => {
        // Debug: check event types
        const types = new Set(data.map(r => r.event_type))
        console.log("Event types in data:", Array.from(types))
        setRelations(data)
      })
      .catch(console.error)
  }, [timeRange])



  // Index states by id
  const stateIndex = useMemo(() => {
    const index = {}
    for (const s of states) index[s.id] = s
    return index
  }, [states])

  // Build arc edges with coordinates and filter by selected event types
  const edges = useMemo(() => {
    return relations
      .filter(r => selectedEventTypes.size === 0 || selectedEventTypes.has(r.event_type))
      .map(r => {
        const src = stateIndex[r.source]
        const tgt = stateIndex[r.target]

        if (!src || !tgt) {
          console.warn("MISSING STATE:", r.source, r.target)
          return null
        }

        const offset = eventOffset(r.event_type)

        return {
          ...r,
          sourcePosition: [src.lon + offset, src.lat],
          targetPosition: [tgt.lon - offset, tgt.lat]
        }
      }).filter(Boolean)
  }, [relations, stateIndex, selectedEventTypes])


  const layers = useMemo(() => [
    // Earth texture
    new TileLayer({
      id: "earth",
      data: "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      renderSubLayers: props => {
        const { west, south, east, north } = props.tile.bbox
        return new BitmapLayer({
          id: `${props.id}-bitmap`,
          image: props.data,
          bounds: [west, south, east, north]
        })
      }
    }),

    // Relations (arcs) with animated flow
    new ArcLayer({
      id: "relations",
      data: edges,

      getSourcePosition: d => d.sourcePosition,
      getTargetPosition: d => d.targetPosition,

      getSourceColor: d => eventColor(d.event_type, 160),
      getTargetColor: d => eventColor(d.event_type, 160),

      getWidth: d => 1 + Math.log1p(d.weight) * 2,
      getHeight: d => 0.25 + Math.log1p(d.weight ?? 1) * 0.15,
      greatCircle: true,
      greatCircleOffset: 0.3,

      // Animated dash effect - more visible
      getDashArray: [8, 8],
      dashJustified: true,
      dashOffset: time,

      updateTriggers: {
        dashOffset: time
      },

      pickable: true,
      onHover: info => {
        if (info.object) {
          setHoverInfo({
            x: info.x,
            y: info.y,
            data: info.object
          })
        } else {
          setHoverInfo(null)
        }
      }
    }),

    // States
    new ScatterplotLayer({
      id: "states",
      data: states,

      getPosition: d => [d.lon, d.lat],
      getRadius: 25_000,
      getFillColor: [0, 0, 154],
      opacity: 0.9,

      pickable: true,

      onHover: info => {
        if (info.object) {
          setHoverInfo({
            x: info.x,
            y: info.y,
            type: "state",
            data: info.object
          })
        } else {
          setHoverInfo(null)
        }
      }
    })

  ], [states, edges, time])

  return (
     
    <div style={{ position: "relative", width: "100vw", height: "100vh" }}>
      
      <div
        style={{
          position: "absolute",
          top: 48,
          left: 12,
          zIndex: 10,
          background: "rgba(0,0,0,0.7)",
          padding: "8px 10px",
          borderRadius: "4px",
          color: "white",
          fontSize: "11px"
        }}
      >
        {Object.entries(EVENT_COLORS).map(([type, color]) => {
          const isSelected = selectedEventTypes.has(type)
          const opacity = selectedEventTypes.size === 0 || isSelected ? 1 : 0.3
          
          return (
            <div 
              key={type} 
              onClick={() => toggleEventType(type)}
              style={{ 
                display: "flex", 
                alignItems: "center", 
                marginBottom: 4,
                cursor: "pointer",
                opacity,
                transition: "opacity 0.2s"
              }}
            >
              <div
                style={{
                  width: 10,
                  height: 10,
                  background: `rgb(${color.join(",")})`,
                  marginRight: 6,
                  border: isSelected ? "2px solid white" : "none"
                }}
              />
              <span>{type}</span>
            </div>
          )
        })}
      </div>

      <div
        style={{
          position: "absolute",
          top: 12,
          left: 12,
          zIndex: 10,
          background: "rgba(0,0,0,0.7)",
          padding: "6px 10px",
          borderRadius: "4px",
          color: "white",
          fontSize: "12px"
        }}
      >
        <label style={{ marginRight: 6 }}>Time:</label>
        <select
          value={timeRange}
          onChange={e => setTimeRange(e.target.value)}
          style={{
            background: "black",
            color: "white",
            border: "1px solid #555"
          }}
        >
          <option value="ALL">All</option>
          <option value="7D">Last 7 days</option>
          <option value="30D">Last 30 days</option>
          <option value="90D">Last 90 days</option>
        </select>
      </div>

      <DeckGL
        views={[new GlobeView()]}
        layers={layers}
        initialViewState={{ longitude: 0, latitude: 20, zoom: 0.9 }}
        controller
        style={{ width: "100%", height: "100%", background: "black" }}
      />

      {hoverInfo && (
        <div
          style={{
            position: "absolute",
            left: hoverInfo.x + 8,
            top: hoverInfo.y + 8,
            background: "rgba(0,0,0,0.8)",
            color: "white",
            padding: "6px 8px",
            fontSize: "12px",
            borderRadius: "4px",
            pointerEvents: "none",
            maxWidth: "240px"
          }}
        >
          {hoverInfo.type === "state" ? (
            <>
              <div><strong>{hoverInfo.data.name || hoverInfo.data.id}</strong></div>
              <div>Code: {hoverInfo.data.id}</div>
            </>
          ) : (
            <>
              <div><strong>{hoverInfo.data.event_type}</strong></div>
              <div>From: {hoverInfo.data.source}</div>
              <div>To: {hoverInfo.data.target}</div>
              <div>Events: {hoverInfo.data.weight}</div>
              {hoverInfo.data.weight != null && (
                <div>Intensity: {hoverInfo.data.weight}</div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
