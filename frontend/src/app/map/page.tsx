"use client"

import dynamic from "next/dynamic"
import "leaflet/dist/leaflet.css"

const Map = dynamic(() => import("@/components/Map"), { ssr: false })

export default function MapPage() {
  return (
    <main style={{ height: "100vh", width: "100vw" }}>
      <Map />
    </main>
  )
} 