from .vertices import Vertices
from src.cityjson.geometry import GeometryPrimitive


class GeometryTemplates:
    def __init__(self, geometries=None, vertices=None):
        self.geometries : list[GeometryPrimitive] = geometries if geometries is not None else []
        self.vertices = vertices if vertices is not None else Vertices()

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.geometries[key]
        return None

    def is_empty(self):
        return len(self.geometries) == 0

    def add_template(self, city_geometry: GeometryPrimitive):
        # todo check if the template already exists (not only with the adress)
        if city_geometry not in self.geometries:
            self.geometries.append(city_geometry)
        return self.geometries.index(city_geometry)

