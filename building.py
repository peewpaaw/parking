import math
from geopy.distance import geodesic
from geopy.point import Point
from scipy.spatial import ConvexHull
import numpy as np
from typing import List, Tuple

class Building:
    def __init__(self, nodes: List[List[float]]):
        """
        Инициализация здания.
        
        Args:
            nodes: Список точек в формате [[lat, lon], [lat, lon], ...]
        """
        self.nodes = nodes

    def _extend_line(self, point1: List[float], point2: List[float], extension_meters: float) -> Tuple[List[float], List[float]]:
        """
        Продлевает линию на заданное расстояние в обе стороны.
        
        Args:
            point1: Начальная точка [lat, lon]
            point2: Конечная точка [lat, lon]
            extension_meters: Расстояние продления в метрах
            
        Returns:
            Tuple из двух точек: начало и конец продленной линии
        """
        p1 = Point(point1[0], point1[1])
        p2 = Point(point2[0], point2[1])
        
        # Получаем азимут между точками
        initial_bearing = self._calculate_initial_compass_bearing(point1, point2)
        #final_bearing = initial_bearing + 180 % 360
        final_bearing = final_bearing + 180
        
        extended_p1 = geodesic(kilometers=extension_meters/1000).destination(p1, final_bearing)
        extended_p2 = geodesic(kilometers=extension_meters/1000).destination(p2, initial_bearing)
        
        return (
            [extended_p1.latitude, extended_p1.longitude],
            [extended_p2.latitude, extended_p2.longitude]
        )

    def _get_all_lines(self) -> List[List[List[float]]]:
        """
        Возвращает все возможные линии между точками здания.
        
        Returns:
            Список линий в формате [[[lat1, lon1], [lat2, lon2]], ...]
        """
        return [
            [self.nodes[i], self.nodes[j]]
            for i in range(len(self.nodes))
            for j in range(i + 1, len(self.nodes))
        ]

    def get_accident_area(self, extension_meters: float) -> List[List[float]]:
        """
        Возвращает точки, образующие область возможного происшествия.
        
        Args:
            extension_meters: Расстояние в метрах, на которое продлеваются линии
            
        Returns:
            Список уникальных точек в формате [[lat1, lon1], [lat2, lon2], ...]
        """
        # Получаем все линии
        lines = self._get_all_lines()
        
        # Продлеваем каждую линию
        extended_lines = [
            self._extend_line(line[0], line[1], extension_meters)
            for line in lines
        ]
        
        # Собираем все уникальные точки
        points = set()
        for line in extended_lines:
            points.add(tuple(line[0]))
            points.add(tuple(line[1]))
        
        # Добавляем исходные точки здания
        # for node in self.nodes:
        #     points.add(tuple(node))
        # return [list(point) for point in points]
        accident_area_points = self._get_convex_hull(list(points))
        return accident_area_points   
    
    def _get_convex_hull(self, points: List[float]):
        """
        Строит выпуклую оболочку из расширенных точек.
        
        Args:
            extension_meters (float): Расстояние в метрах для продления линий
            
        Returns:
            list: Список точек выпуклой оболочки в порядке их соединения [[lat1, lon1], [lat2, lon2], ...]
        """
        # Преобразуем в numpy массив
        points_array = np.array(points)
        
        # Строим выпуклую оболочку
        hull = ConvexHull(points_array)
        
        # Получаем индексы вершин выпуклой оболочки
        hull_vertices = hull.vertices
        
        # Создаем список точек выпуклой оболочки в порядке их соединения
        hull_points = []
        for idx in hull_vertices:
            hull_points.append(points[idx])
        
        # Добавляем первую точку в конец для замыкания фигуры
        hull_points.append(hull_points[0])
        
        return hull_points
    
    @staticmethod
    def _calculate_initial_compass_bearing(point1: List[float], point2: List[float]) -> float:
        """
        Рассчитывает начальный азимут между двумя точками.
        
        Args:
            point1: Начальная точка [lat, lon]
            point2: Конечная точка [lat, lon]
            
        Returns:
            Азимут в градусах (0-360)
        """
        lat1 = math.radians(point1[0])
        lon1 = math.radians(point1[1])
        lat2 = math.radians(point2[0])
        lon2 = math.radians(point2[1])

        dLon = lon2 - lon1
        x = math.sin(dLon) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(dLon))

        initial_bearing = math.atan2(x, y)

        # Нормализуем угол в диапазон [0, 360]
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360

        return compass_bearing