from src.cityjson.vertices import Vertices
from src.cityjson.geometry import GeometryPrimitive

import numpy as np


class FakeCity:
    def __init__(self, vertices):
        self.vertices = vertices

    def get_vertices(self):
        return self.vertices


class GeometryTemplate:
    def __init__(self, city, geometries=None, vertices=None):
        self.city = city
        self.geometries : list[GeometryPrimitive] = geometries if geometries is not None else []
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
        city = FakeCity(self.vertices)
        templates_cj = [geometry.to_cj(city) for geometry in self.geometries]
        precision = self.city.precision()
        vertices = np.array(self.vertices._vertices)
        vertices = np.round(vertices, precision)

        return {
            'templates' : templates_cj,
            'vertices-templates' : vertices.tolist()
        }

