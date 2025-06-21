"use client"

import { MapContainer, TileLayer, useMapEvents, Polygon } from "react-leaflet"
import { useState } from "react"
import type { LatLngExpression } from "leaflet"
import "leaflet/dist/leaflet.css"

const center: LatLngExpression = [53.902284, 27.561831] 

interface ClickedData {
  address: string
  osmId: number | null
}

function LocationMarker() {
  const [clickedData, setClickedData] = useState<ClickedData | null>(null)
  const [polygonCoords, setPolygonCoords] = useState<LatLngExpression[] | null>(null)

  const map = useMapEvents({
    async click(e) {
      setPolygonCoords(null) // Очищаем старый полигон при новом клике
      const { lat, lng } = e.latlng
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`,
      )
      const data = await response.json()
      console.log(data)

      setClickedData({
        address: data.display_name,
        osmId: data.osm_type === "way" ? data.osm_id : null,
      })
    },
  })

  const handleAccidentClick = async () => {
    if (!clickedData?.osmId) return

    const apiUrl = process.env.NEXT_PUBLIC_API_URL
    const wayId = clickedData.osmId
    const url = `${apiUrl}/api/v1/accidents/accident_area?way_id=${wayId}&extension_meters=50`

    try {
      const response = await fetch(url)
      const result = await response.json()
      console.log("Ответ от бэкенда:", result)
      setPolygonCoords(result) // Сохраняем координаты для отрисовки полигона
    } catch (error) {
      console.error("Ошибка при запросе к бэкенду:", error)
    }
  }

  return (
    <>
      {clickedData ? (
        <div className="absolute bottom-4 right-4 z-[1000] bg-white p-4 rounded-md shadow-lg max-w-sm">
          <p className="font-bold">Выбранный объект:</p>
          <p>
            <strong>Адрес:</strong> {clickedData.address}
          </p>
          {clickedData.osmId && (
            <p>
              <strong>Way ID:</strong> {clickedData.osmId}
            </p>
          )}
          <button
            onClick={handleAccidentClick}
            disabled={!clickedData.osmId}
            className="mt-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Авария
          </button>
        </div>
      ) : null}
      {polygonCoords && <Polygon pathOptions={{ color: "blue" }} positions={polygonCoords} />}
    </>
  )
}

export default function Map() {
  return (
    <div className="relative h-screen w-screen">
      <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <LocationMarker />
      </MapContainer>
    </div>
  )
} 