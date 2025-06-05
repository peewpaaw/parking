from fastapi import APIRouter, HTTPException
from typing import List, Tuple

from ..services.osm_client import OSMClient
from ..services.building import Building

router = APIRouter()
osm_client = OSMClient()

@router.get("/accident_area", response_model=List[Tuple[float, float]])
async def get_accidents_area(way_id: int, extension_meters: float = 1000):
    coordinates = osm_client.get_way_nodes_coordinates(way_id)
    if not coordinates:
        raise HTTPException(status_code=404, detail="Way not found or has no coordinates")
    
    # Создаем объект Building с полученными координатами
    building = Building(coordinates)
    
    # Получаем точки области возможного происшествия
    accident_area = building.get_accident_area(extension_meters)
    
    return accident_area 