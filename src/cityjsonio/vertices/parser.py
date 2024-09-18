import numpy as np

from src.cityjson import City, Vertices


class VerticesParser:
    def __init__(self, city: City):
        self.city = city
        self.translate = city.origin
        self.scale = city.scale
        self.precision = city.precision()

    # data contains cityjson['vertices']
    def parse(self, data):
        if len(data) == 0:
            return Vertices(self.city)
        vertices = np.array(data)
        vertices = (vertices * np.array(self.scale)) + np.array(self.translate)
        if self.precision is not None:
            vertices = np.round(vertices, self.precision)
        vertices = vertices.tolist()
        return Vertices(self.city, vertices)

