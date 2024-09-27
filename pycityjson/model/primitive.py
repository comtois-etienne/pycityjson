# https://www.cityjson.org/dev/geom-arrays/


from .matrix import TransformationMatrix
from .semantic import Semantic


class Primitive:
    def get_children(self):
        return self.children

    def __str__(self):
        return f'{self.get_type()}(len={len(self.children)})'

    def __repr__(self) -> str:
        children = ', '.join([repr(child) for child in self.children])
        return f'{self.get_type()}({children})'

    def transform(self, matrix: TransformationMatrix, center=[0, 0, 0]):
        for child in self.children:
            child.transform(matrix, center)

    def get_type(self) -> str:
        # todo have proper types instead of strings
        return self.type

    def copy(self):
        return self.__class__([child.copy() for child in self.children])

    def add_child(self, child):
        self.children.append(child)

    def index_vertices(self, vertices):
        return [child.index_vertices(vertices) for child in self.children]

    def get_vertices(self, flatten=False):
        vertices = []
        for child in self.children:
            if flatten:
                vertices += child.get_vertices(flatten)
            else:
                vertices.append(child.get_vertices(flatten))
        return vertices

    def get_min_max(self):
        vertices = self.get_vertices(flatten=True)
        min_x = min([vertex[0] for vertex in vertices])
        min_y = min([vertex[1] for vertex in vertices])
        min_z = min([vertex[2] for vertex in vertices])
        max_x = max([vertex[0] for vertex in vertices])
        max_y = max([vertex[1] for vertex in vertices])
        max_z = max([vertex[2] for vertex in vertices])
        return [min_x, min_y, min_z], [max_x, max_y, max_z]

    def normalize(self):
        _min, _ = self.get_min_max()
        matrix = TransformationMatrix().translate([-_min[0], -_min[1], -_min[2]])
        self.transform(matrix)

        _min, _max = self.get_min_max()
        scale = [
            1 / (_max[0] - _min[0]),
            1 / (_max[1] - _min[1]),
            1 / (_max[2] - _min[2]),
        ]
        matrix = TransformationMatrix().scale(scale)
        self.transform(matrix)

        matrix = TransformationMatrix().translate([-0.5, -0.5, 0])
        self.transform(matrix)

    def get_semantic_surfaces(self):
        return None

    def get_semantic_values(self, semantics):
        return [child.get_semantic_values(semantics) for child in self.children]


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __repr__(self):
        return f'Point({self.x}, {self.y}, {self.z})'

    def copy(self):
        return self.__class__(self.x, self.y, self.z)

    def transform(self, matrix: TransformationMatrix, center=[0, 0, 0]):
        vertex = [self.x - center[0], self.y - center[1], self.z - center[2]]
        vertex = matrix.reproject_vertex(vertex)
        self.x = vertex[0] + center[0]
        self.y = vertex[1] + center[1]
        self.z = vertex[2] + center[2]

    def to_list(self):
        return [self.x, self.y, self.z]

    def index_vertices(self, vertices):
        index = vertices.add(self.to_list())
        return index


# collection of points -> used to create shape
class MultiPoint(Primitive):
    __ptype = 'MultiPoint'
    __depth = 1

    def __init__(self, points: list[Point] = None):
        self.type = self.__ptype
        self.children = [] if points is None else points

    def get_vertices(self, flatten=False):
        return [point.to_list() for point in self.children]

    def get_semantic_values(self, semantics):
        return None


#### This is a surface containing the semantic ####
# first multi point is the exterior ring
# the rest are interior rings
class MultiLineString(Primitive):
    __ptype = 'MultiLineString'
    __depth = 2

    def __init__(self, faces: list[MultiPoint] = None, semantic: Semantic = None):
        self.type = self.__ptype
        self.semantic = semantic
        self.children = [] if faces is None else faces

    def __repr__(self):
        if self.semantic is None:
            return super().__repr__()
        children = ', '.join([repr(child) for child in self.children])
        semantic = self.semantic.to_dict()
        return f'{self.get_type()}((Semantic({semantic}))=({children}))'

    def set_exterior_face(self, exterior: MultiPoint):
        if len(self.children) == 0:
            self.children.append(exterior)
        else:
            self.children[0] = exterior

    def get_semantic_cj(self):
        return self.semantic.to_dict() if self.semantic is not None else None

    def get_semantic_values(self, semantics):
        for i in range(len(semantics)):
            if semantics[i] == self.semantic:
                return i
        return None


# Used to create a landscape of a building wall
class MultiSurface(Primitive):
    __ptype = 'MultiSurface'  # separate surfaces with holes
    __ptype_a = 'MultiSurface'  # separate surfaces with holes
    __ptype_b = 'CompositeSurface'  # adjacents surfaces without overlap
    __depth = 3

    def __init__(self, surfaces: list[MultiLineString] = None):
        self.type = self.__ptype
        self.children = [] if surfaces is None else surfaces

    def get_semantic_surfaces(self):
        semantics = {}
        for surface in self.children:
            semantic = surface.get_semantic_cj()
            if semantic is None:
                return None
            semantics[surface.semantic['uuid']] = semantic
        return list(semantics.values())


# Used to create a building
class Solid(Primitive):
    __ptype = 'Solid'
    __depth = 4

    def __init__(self, multi_surfaces: list[MultiSurface] = None):
        self.type = self.__ptype
        self.children = [] if multi_surfaces is None else multi_surfaces

    def get_semantic_surfaces(self):
        semantics = {}
        for multi_surface in self.children:
            for surface in multi_surface.children:
                semantic = surface.get_semantic_cj()
                if semantic is None:
                    return None
                semantics[surface.semantic['uuid']] = semantic
        return list(semantics.values())


class MultiSolid(Primitive):
    __ptype = 'MultiSolid'
    __ptype_a = 'MultiSolid'  # separate solids
    __ptype_b = 'CompositeSolid'  # adjacents solids
    __depth = 5

    def __init__(self, solids: list[Solid] = None):
        self.type = self.__ptype
        self.children = [] if solids is None else solids

    def get_semantic_surfaces(self):
        semantics = {}
        for solid in self.children:
            for multi_surface in solid.children:
                for surface in multi_surface.children:
                    semantic = surface.get_semantic_cj()
                    if semantic is None:
                        return None
                    semantics[surface.semantic['uuid']] = semantic
        return list(semantics.values())
