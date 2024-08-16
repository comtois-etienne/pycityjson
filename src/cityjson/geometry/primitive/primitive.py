# https://www.cityjson.org/dev/geom-arrays/


from .semantic import Semantic


class Primitive:
    def __str__(self):
        return f"{self.get_type()}(len={len(self.children)})"

    def __repr__(self) -> str:
        children = ', '.join([repr(child) for child in self.children])
        return f"{self.get_type()}({children})"

    def get_type(self):
        return self.type

    def to_cj(self, vertices):
        return [child.to_cj(vertices) for child in self.children]

    def add_child(self, child):
        self.children.append(child)

    def get_vertices(self, flatten=False):
        vertices = []
        for child in self.children:
            if flatten:
                vertices += child.get_vertices(flatten)
            else:
                vertices.append(child.get_vertices(flatten))
        return vertices

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
        return f"({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def to_list(self):
        return [self.x, self.y, self.z]

    def to_cj(self, vertices):
        index = vertices.add(self.to_list())
        return index


# collection of points -> used to create shape
class MultiPoint(Primitive):
    __ptype = "MultiPoint"
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
    __ptype = "MultiLineString"
    __depth = 2

    def __init__(self, faces: list[MultiPoint] = None, semantic: Semantic=None):
        self.type = self.__ptype
        self.semantic = semantic
        self.children = [] if faces is None else faces

    def __repr__(self):
        if self.semantic is None:
            return super().__repr__()
        children = ', '.join([repr(child) for child in self.children])
        semantic = self.semantic.to_cj()
        return f"{self.get_type()}((Semantic({semantic}))=({children}))"

    def set_exterior_face(self, exterior: MultiPoint):
        if len(self.children) == 0:
            self.children.append(exterior)
        else:
            self.children[0] = exterior
    
    def get_semantic_cj(self):
        return self.semantic.to_cj() if self.semantic is not None else None
    
    def get_semantic_values(self, semantics):
        for i in range(len(semantics)):
            if semantics[i] == self.semantic:
                return i
        return None


# Used to create a landscape of a building wall
class MultiSurface(Primitive):
    __ptype = "MultiSurface" # separate surfaces with holes
    __ptype_a = "MultiSurface" # separate surfaces with holes
    __ptype_b = "CompositeSurface" # adjacents surfaces without overlap
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
    __ptype = "Solid"
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
    __ptype = "MultiSolid"
    __ptype_a = "MultiSolid" # separate solids
    __ptype_b = "CompositeSolid" # adjacents solids
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

