import requests
from typing import List, Tuple, Optional

class OSMClient:
    def __init__(self, base_url: str = "https://overpass-api.de/api/interpreter"):
        self.base_url = base_url

    def get_way_nodes_coordinates(self, way_id: int) -> Optional[List[Tuple[float, float]]]:
        """
        Получает список координат нодов для way
        
        Args:
            way_id: ID way в OSM
            
        Returns:
            Список кортежей (lat, lon) для каждого нода или None в случае ошибки
        """
        query = f"""
        [out:json];
        way({way_id});
        out body;
        >;
        out skel qt;
        """
        
        try:
            response = requests.post(self.base_url, data=query)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("elements"):
                return None
                
            # Находим way среди элементов
            way_data = next(
                (el for el in data["elements"] if el["type"] == "way"),
                None
            )
            if not way_data:
                return None
                
            # Создаем словарь нодов для быстрого доступа
            nodes_dict = {
                node["id"]: (node["lat"], node["lon"])
                for node in data["elements"]
                if node["type"] == "node"
            }
            
            # Получаем координаты нодов в правильном порядке
            coordinates = [
                nodes_dict[node_id]
                for node_id in way_data.get("nodes", [])
                if node_id in nodes_dict
            ]
            
            return coordinates
            
        except requests.RequestException as e:
            print(f"Error fetching way data: {e}")
            return None