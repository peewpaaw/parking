from geopy.distance import geodesic
from geopy.point import Point
import math
from scipy.spatial import ConvexHull
import numpy as np

class Building:
    def __init__(self, nodes):
        self.nodes = nodes  # список точек в формате [[lat, lon], [lat, lon], ...]
    
    def get_lines(self):
        """
        Возвращает список всех возможных прямых между точками здания.
        Каждая прямая представлена как [[lat1, lon1], [lat2, lon2]]
        """
        lines = []
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                lines.append([self.nodes[i], self.nodes[j]])
        return lines
    
    def get_extended_lines(self, extension_meters):
        """
        Продлевает все линии на заданное расстояние в обе стороны.
        
        Args:
            extension_meters (float): Расстояние в метрах, на которое нужно продлить линии
            
        Returns:
            list: Список продленных линий в формате [[[lat1, lon1], [lat2, lon2]], ...]
        """
        lines = self.get_lines()
        extended_lines = []
        
        for line in lines:
            point1, point2 = line
            
            # Создаем Point объекты для работы с geopy
            p1 = Point(point1[0], point1[1])
            p2 = Point(point2[0], point2[1])
            
            # Получаем азимут (направление) линии
            initial_bearing = geodesic(p1, p2).initial_bearing
            
            # Получаем конечный азимут (в обратном направлении)
            final_bearing = (initial_bearing + 180) % 360
            
            # Продлеваем линию в обоих направлениях
            extended_p1 = geodesic(kilometers=extension_meters/1000).destination(p1, final_bearing)
            extended_p2 = geodesic(kilometers=extension_meters/1000).destination(p2, initial_bearing)
            
            # Добавляем продленную линию
            extended_lines.append([
                [extended_p1.latitude, extended_p1.longitude],
                [extended_p2.latitude, extended_p2.longitude]
            ])
        
        return extended_lines
    
    def get_extended_points(self, extension_meters):
        """
        Преобразует расширенные линии в список уникальных точек.
        
        Args:
            extension_meters (float): Расстояние в метрах для продления линий
            
        Returns:
            list: Список уникальных точек в формате [[lat1, lon1], [lat2, lon2], ...]
        """
        extended_lines = self.get_extended_lines(extension_meters)
        points = set()
        
        # Добавляем все точки из линий в множество для уникальности
        for line in extended_lines:
            points.add(tuple(line[0]))  # первая точка линии
            points.add(tuple(line[1]))  # вторая точка линии
        
        # Преобразуем обратно в список списков
        return [list(point) for point in points]
    
    def get_convex_hull(self, extension_meters):
        """
        Строит выпуклую оболочку из расширенных точек.
        
        Args:
            extension_meters (float): Расстояние в метрах для продления линий
            
        Returns:
            list: Список точек выпуклой оболочки в порядке их соединения [[lat1, lon1], [lat2, lon2], ...]
        """
        # Получаем все точки
        points = self.get_extended_points(extension_meters)
        
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
    