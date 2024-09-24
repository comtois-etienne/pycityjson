from typing import Any, TypeAlias

Vertex: TypeAlias = list[float]


class Vertices:
    def __init__(self, vertices: list[Vertex] = None, precision: int = 3, start_index: int = 0):
        """
        :param vertices: Initial vertices of the collection
        :param precision: the number of decimal places to round the vertices. Must be a positive integer [0, infinity]
        TODO: check if comment good?
        :param start_index: N based index to start the indexation of the vertices at 0 or
        """
        self.start_index = start_index
        self.__precision = precision
        self._vertices = []
        # Dict to store the index of the vertices for performance reasons
        self._vertices_dict: dict[str, int] = {}

        vertices = vertices if vertices is not None else []

        for vertex in vertices:
            self.add(vertex)

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

    def __contains__(self, item: Any) -> bool:
        if not isinstance(item, list) and len(item) != 3:
            return False

        return self.__vertex_to_string(item) in self._vertices_dict

    def get_index(self, vertex: Vertex) -> int | None:
        if vertex not in self:
            return None

        return self._vertices_dict[self.__vertex_to_string(vertex)] + self.start_index

    def get_vertice(self, index):
        if index < 0 or index >= len(self._vertices):
            return None
        vertex = self._vertices[index]
        return [vertex[0], vertex[1], vertex[2]]

    def get_min(self, axis=0):
        return min(self.__get_axis(axis))

    def get_max(self, axis=0):
        return max(self.__get_axis(axis))

    def add(self, vertex: Vertex) -> int:
        """
        Add a vertex to the collection with a given precision. Will round the vertex to the precision given in the
        constructor.
        """
        vertex = [round(coord, self.__precision) for coord in vertex]

        if vertex not in self:
            self._vertices_dict[self.__vertex_to_string(vertex)] = len(self._vertices)
            self._vertices.append(vertex)

        return self.get_index(vertex)

    def __get_axis(self, axis=0):
        return [coord[axis] for coord in self._vertices]

    def tolist(self):
        return self._vertices

    @staticmethod
    def __vertex_to_string(vertex: Vertex):
        return f'{vertex[0]} {vertex[1]} {vertex[2]}'

    @staticmethod
    def __string_to_vertice(string: str) -> Vertex:
        return [float(x) for x in string.split(' ')]
