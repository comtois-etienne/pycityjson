import numpy as np


def vertice_to_string(vertice):
    return f"{vertice[0]} {vertice[1]} {vertice[2]}"


def string_to_vertice(string):
    return [float(x) for x in string.split(' ')]


class Vertices:
    def __init__(self, city, vertices=None):
        self.city = city
        self._vertices = [] if vertices is None else vertices
        self._vertices_dict = {vertice_to_string(vertice): i for i, vertice in enumerate(self._vertices)}

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.get_vertice(item)
        elif isinstance(item, list):
            return self.get_index(item)
        return None

    def __len__(self):
        return len(self._vertices)

    def __iter__(self):
        return iter(self._vertices)

    def __contains__(self, item):
        if not isinstance(item, list) and len(item) != 3:
            return False
        return vertice_to_string(item) in self._vertices_dict

    def get_index(self, vertice):
        if vertice not in self:
            return None
        return self._vertices_dict[vertice_to_string(vertice)]

    def get_vertice(self, index):
        if index < 0 or index >= len(self._vertices):
            return None
        vertice = self._vertices[index]
        return [vertice[0], vertice[1], vertice[2]]

    def get_min(self, axis=0):
        return min(self.__get_axis(axis))

    def get_max(self, axis=0):
        return max(self.__get_axis(axis))

    def add(self, vertice):
        if vertice not in self:
            self._vertices_dict[vertice_to_string(vertice)] = len(self._vertices)
            self._vertices.append(vertice)
        return self.get_index(vertice)

    def __get_axis(self, axis=0):
        return [coord[axis] for coord in self._vertices]

    def to_cj(self):
        vertices = np.array(self._vertices)
        vertices = ( vertices - np.array(self.city.origin) ) / np.array(self.city.scale)
        vertices = np.round(vertices).astype(int)
        return vertices.tolist()

