from .geometry import GeometryPrimitive
from .vertices import Vertices


class GeometryTemplates:
    def __init__(self, geometries: list[GeometryPrimitive], vertices: Vertices):
        self.geometries = geometries
        self.vertices = vertices

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
