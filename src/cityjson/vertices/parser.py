import numpy as np
from .vertices import Vertices


class VerticesParser:
    def __init__(self, city):
        self.city = city
        self.translate = city.origin()
        self.scale = city.scale()
        self.precision = city.precision()

    # data contains cityjson['vertices']
    def parse(self, data):
        vertices = np.array(data)
        vertices = (vertices * np.array(self.scale)) + np.array(self.translate)
        vertices = np.round(vertices, self.precision)
        vertices = vertices.tolist()
        return Vertices(self.city, vertices)

