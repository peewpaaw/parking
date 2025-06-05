from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .services.osm_client import OSMClient
from .services.building import Building
from .api.router import api_router
from .core import config

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

root_router = APIRouter()

app.include_router(root_router)
app.include_router(api_router, prefix=config.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Parking API"}


# @app.get("/way/{way_id}/coordinates", response_model=List[Tuple[float, float]])
# async def get_way_coordinates(way_id: int):
#     coordinates = osm_client.get_way_nodes_coordinates(way_id)
#     if not coordinates:
#         raise HTTPException(status_code=404, detail="Way not found or has no coordinates")
#     return coordinates 
