from src.cityjson.vertices import Vertices
from src.cityjson.geometry import Geometry


class GeometryTemplate:
    def __init__(self, city, geometries=None, vertices=None):
        self.geometries : list[Geometry] = geometries if geometries is not None else []
        self.vertices = vertices if vertices is not None else Vertices(city)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.geometries[key]
        return None

    def is_empty(self):
        return len(self.geometries) == 0

    def add_template(self, city_geometry):
        # todo check if the template already exists (not only with the adress)
        if city_geometry not in self.geometries:
            self.geometries.append(city_geometry)
        return self.geometries.index(city_geometry)

    def to_cj(self):
        templates_cj = [geometry.to_cj(self.vertices) for geometry in self.geometries]
        return {
            'templates' : templates_cj,
            'vertices-templates' : self.vertices._vertices
        }

