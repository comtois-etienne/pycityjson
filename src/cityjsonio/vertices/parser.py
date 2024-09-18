import numpy as np

from src.cityjson import City, Vertices


class VerticesParser:
    def __init__(self, origin, scale, precision):
        self.translate = origin
        self.scale = scale
        self.precision = precision

    # data contains cityjson['vertices']
    def parse(self, data):
        if len(data) == 0:
            return Vertices()
        vertices = np.array(data)
        vertices = (vertices * np.array(self.scale)) + np.array(self.translate)
        if self.precision is not None:
            vertices = np.round(vertices, self.precision)
        vertices = vertices.tolist()
        return Vertices(vertices)

