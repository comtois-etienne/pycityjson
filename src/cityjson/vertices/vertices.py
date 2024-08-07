import numpy as np


class Vertices:
    def __init__(self, city, vertices=[]):
        self.city = city
        self._vertices = vertices

    def __getitem__(self, index):
        if isinstance(index, int):
            return self._vertices[index]
        else:
            return self.get(index[0], index[1], index[2])

    def __len__(self):
        return len(self._vertices)
    
    def __iter__(self):
        return iter(self._vertices)
    
    def __contains__(self, item):
        return item in self._vertices
    
    def exists(self, x, y, z):
        return [x, y, z] in self._vertices
    
    def get(self, x, y, z):
        coord = [x, y, z]
        if self.exists(x, y, z):
            return self._vertices.index(coord)
        return None

    def get_min(self, axis=0):
        return min(self.get_axis(axis))

    def get_max(self, axis=0):
        return max(self.get_axis(axis))

    def add(self, x, y, z):
        coord = [x, y, z]
        if not self.exists(x, y, z):
            self._vertices.append(coord)
        return self.get(x, y, z)

    def get_axis(self, axis=0):
        return [coord[axis] for coord in self._vertices]

    def to_cj(self):
        vertices = np.array(self._vertices)
        vertices = ( vertices - np.array(self.city.origin) ) / np.array(self.city.scale)
        vertices = np.round(vertices).astype(int)
        return vertices.tolist()

