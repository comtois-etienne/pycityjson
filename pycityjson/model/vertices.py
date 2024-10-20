from copy import copy
from typing import TypeAlias

import numpy as np

Vertex: TypeAlias = list[float]


class Vertices:
    """
    Container for vertices with a given precision.
    Will round the given vertices.
    """

    def __init__(self, vertices: list[Vertex] = None, precision: int = 3, start_index: int = 0):
        """
        :param vertices: Initial vertices of the collection
        :param precision: the number of decimal places to round the vertices. Must be a positive integer [0, infinity]
        :param start_index: start index for the vertices (zero based by default)
        """
        self.start_index = start_index
        self.__precision = precision
        self.__vertices = []
        # Dict to store the index of the vertices for performance reasons
        self.__vertices_dict: dict[str, int] = {}

        vertices = vertices if vertices is not None else []

        for vertex in vertices:
            self.add(vertex)

    def __getitem__(self, item: Vertex | int) -> Vertex | None:
        """
        Returns the vertex at the given index or the index of the given vertex
        :param item: Vertex or index
        :return: Vertex if item is an index, index if item is a vertex. None if the item is not in the collection
        """
        if isinstance(item, int):
            return self.get_vertice(item)
        elif isinstance(item, list):
            return self.get_index(item)
        return None

    def __len__(self) -> int:
        """
        Returns the number of vertices in the collection
        """
        return len(self.__vertices)

    def __iter__(self):
        """
        Iterator for the vertices
        """
        return iter(self.__vertices)

    def __contains__(self, item: Vertex) -> bool:
        """
        :param item: Vertex to check if it is in the collection
        :return: True if the vertex is in the collection, False otherwise
        """
        if not isinstance(item, list) and len(item) != 3:
            return False
        return self.__vertex_to_string(item) in self.__vertices_dict

    def get_index(self, vertex: Vertex) -> int | None:
        """
        :param vertex: Vertex to get the index of
        :return: Index of the vertex in the collection. None if the vertex is not in the collection
        """
        if vertex not in self:
            return None
        return self.__vertices_dict[self.__vertex_to_string(vertex)] + self.start_index

    def get_vertice(self, index: int) -> Vertex | None:
        """
        :param index: Index of the vertex to get
        :return: Vertex at the given index. None if the index is out of bounds
        """
        if index < 0 or index >= len(self.__vertices):
            return None
        vertex = self.__vertices[index]
        return [vertex[0], vertex[1], vertex[2]]

    def get_min(self) -> list[float]:
        """
        :return: Minimum value of the given axis (x, y, z)
        """
        vertices = np.array(self.__vertices)
        return np.min(vertices, axis=0).tolist()

    def get_max(self) -> float:
        """
        :return: Maximum value of the given axis (x, y, z)
        """
        vertices = np.array(self.__vertices)
        return np.max(vertices, axis=0)

    def add(self, vertex: Vertex) -> int:
        """
        Add a vertex to the collection with a given precision. Will round the vertex to the precision given in the
        constructor.
        """
        vertex = [round(coord, self.__precision) for coord in vertex]

        if vertex not in self:
            self.__vertices_dict[self.__vertex_to_string(vertex)] = len(self.__vertices)
            self.__vertices.append(vertex)

        return self.get_index(vertex)

    def get_axis(self, axis: int) -> list[float]:
        """
        :param axis: Axis to get the values of (0=x, 1=y, 2=z)
        """
        v = np.array(self.__vertices)
        return v[:, axis].tolist()

    def tolist(self) -> list[Vertex]:
        """
        :return: List of vertices
        """
        return copy(self.__vertices)

    @staticmethod
    def __vertex_to_string(vertex: Vertex) -> str:
        """
        Used to store the vertices in a dictionary for performance reasons
        :param vertex: Vertex to convert to a string in the format 'x y z'
        """
        return f'{vertex[0]} {vertex[1]} {vertex[2]}'

    @staticmethod
    def __string_to_vertice(string: str) -> Vertex:
        """
        Reverses the __vertex_to_string method
        :param string: String in the format 'x y z'
        """
        return [float(x) for x in string.split(' ')]
