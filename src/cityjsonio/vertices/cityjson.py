import numpy as np

from src.cityjson import Vertices


class VerticesToCityJsonSerializer:
    def __init__(self, vertices: Vertices, origin=None, scale=None):
        self.vertices = vertices
        self.origin = [0, 0, 0] if origin is None else origin
        self.scale = [0.001, 0.001, 0.001] if scale is None else scale

    def serialize(self) -> list:
        vertices = np.array(self.vertices._vertices)
        vertices = ( vertices - np.array(self.origin) ) / np.array(self.scale)
        vertices = np.round(vertices).astype(int)
        return vertices.tolist()

