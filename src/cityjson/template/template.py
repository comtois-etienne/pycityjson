from src.cityjson.vertices import Vertices
from src.cityjson.geometry import CityPrimitive

class GeometryTemplate:
    def __init__(self, city, templates=None, vertices=None):
        self.templates : list[CityPrimitive] = templates if templates is not None else []
        self.vertices = vertices if vertices is not None else Vertices(city)

    def is_empty(self):
        return len(self.templates) == 0

    def to_cj(self):
        templates_cj = [template.to_cj(self.vertices) for template in self.templates]
        return {
            'templates' : templates_cj,
            'vertices-templates' : self.vertices._vertices
        }

