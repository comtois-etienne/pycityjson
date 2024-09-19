import numpy as np

from src.cityjson import Vertices
from src.cityjson.template import GeometryTemplates

from src.cityjsonio.geometry import GeometryPrimitiveToCityJsonSerializer as GeometrySerializer


class GeometryTemplateToCityJsonSerializer:
    def __init__(self, geometry_template: GeometryTemplates, precision):
        self.geometry_template = geometry_template
        self.serializer = GeometrySerializer(geometry_template.vertices)
        self.precision = precision

    def serialize(self) -> dict:
        templates = [self.serializer.serialize(geometry) for geometry in self.geometry_template.geometries]
        vertices = np.array(self.geometry_template.vertices._vertices)
        vertices = np.round(vertices, self.precision)

        return {
            'templates' : templates,
            'vertices-templates' : vertices.tolist()
        }

