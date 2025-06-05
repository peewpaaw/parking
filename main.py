from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from osm_client import OSMClient
from building import Building
from typing import List, Tuple

app = FastAPI(title="Parking API")
osm_client = OSMClient()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Parking API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/way/{way_id}/coordinates", response_model=List[Tuple[float, float]])
async def get_way_coordinates(way_id: int):
    coordinates = osm_client.get_way_nodes_coordinates(way_id)
    if not coordinates:
        raise HTTPException(status_code=404, detail="Way not found or has no coordinates")
    return coordinates 

@app.get("/way/{way_id}/accident_area", response_model=List[Tuple[float, float]])
async def get_accidents_area(way_id: int, extension_meters: float = 1000):
    coordinates = osm_client.get_way_nodes_coordinates(way_id)
    if not coordinates:
        raise HTTPException(status_code=404, detail="Way not found or has no coordinates")
    
    # Создаем объект Building с полученными координатами
    building = Building(coordinates)
    
    # Получаем точки области возможного происшествия
    accident_area = building.get_accident_area(extension_meters)
    
    return accident_area 