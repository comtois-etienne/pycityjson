# https://www.cityjson.org/dev/geom-arrays/


from .semantic import Semantic


class Primitive:
    def get_type(self):
        pass

    def to_cj(self, vertices):
        pass

    def add_child(self, child):
        pass

    def get_semantic_surfaces(self):
        return None

    def get_semantic_values(self, semantics):
        return None


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.z})"

    def to_cj(self, vertices):
        index = vertices.add([self.x, self.y, self.z])
        return index


# collection of points -> used to create shape
class MultiPoint(Primitive):
    __type = "MultiPoint"
    __depth = 1

    def __init__(self, points: list[Point] = None):
        self.children = [] if points is None else points

    def __repr__(self):
        return f"{self.__type}_{self.__depth}(len{len(self.children)})"

    def get_type(self):
        return self.__type

    def add_child(self, point: Point):
        self.children.append(point)

    def to_cj(self, vertices):
        return [point.to_cj(vertices) for point in self.children]


#### This is a surface containing the semantic ####
# first multi point is the exterior ring
# the rest are interior rings
class MultiLineString(Primitive):
    __type = "MultiLineString"
    __depth = 2

    def __init__(self, faces: list[MultiPoint] = None, semantic=None):
        self.semantic = semantic
        self.children = [] if faces is None else faces

    def __repr__(self):
        return f"{self.__type}_{self.__depth}(len{len(self.children)})"

    def get_type(self):
        return self.__type

    def add_child(self, face: MultiPoint):
        self.children.append(face)

    def set_exterior_face(self, exterior: MultiPoint):
        if len(self.children) == 0:
            self.children.append(exterior)
        else:
            self.children[0] = exterior

    def to_cj(self, vertices):
        return [face.to_cj(vertices) for face in self.children]
    
    def get_semantic_cj(self):
        return self.semantic.to_cj()
    
    def get_semantic_values(self, semantics):
        for i in range(len(semantics)):
            if semantics[i] == self.semantic:
                return i
        return None


# Used to create a landscape of a building wall
class MultiSurface(Primitive):
    __type = "MultiSurface" # separate surfaces with holes
    __type_a = "MultiSurface" # separate surfaces with holes
    __type_b = "CompositeSurface" # adjacents surfaces without overlap
    __depth = 3

    def __init__(self, surfaces: list[MultiLineString] = None):
        self.children = [] if surfaces is None else surfaces

    def __repr__(self):
        return f"{self.__type}_{self.__depth}(len{len(self.children)})"

    def get_type(self):
        return self.__type

    def add_child(self, surface: MultiLineString):
        self.children.append(surface)

    def to_cj(self, vertices):
        return [surface.to_cj(vertices) for surface in self.children]
    
    def get_semantic_surfaces(self):
        semantics = {}
        for surface in self.children:
            semantics[surface.semantic['uuid']] = surface.get_semantic_cj()
        return list(semantics.values())

    # depth = 1
    def get_semantic_values(self, semantics):
        return [surface.get_semantic_values(semantics) for surface in self.children]


# Used to create a building
class Solid(Primitive):
    __type = "Solid"
    __depth = 4

    def __init__(self, multi_surfaces: list[MultiSurface] = None):
        self.children = [] if multi_surfaces is None else multi_surfaces

    def __repr__(self):
        return f"{self.__type}_{self.__depth}(len{len(self.children)})"

    def get_type(self):
        return self.__type

    def add_child(self, multi_surface: MultiSurface):
        self.children.append(multi_surface)

    def to_cj(self, vertices):
        return [multi_surface.to_cj(vertices) for multi_surface in self.children]
    
    def get_semantic_surfaces(self):
        semantics = {}
        for multi_surface in self.children:
            for surface in multi_surface.children:
                semantics[surface.semantic['uuid']] = surface.get_semantic_cj()
        return list(semantics.values())

    # depth = 2
    def get_semantic_values(self, semantics):
        return [multi_surface.get_semantic_values(semantics) for multi_surface in self.children]


class MultiSolid(Primitive):
    __type = "MultiSolid"
    __type_a = "MultiSolid" # separate solids
    __type_b = "CompositeSolid" # adjacents solids
    __depth = 5

    def __init__(self, solids: list[Solid] = None):
        self.children = [] if solids is None else solids

    def __repr__(self):
        return f"{self.__type}_{self.__depth}(len{len(self.children)})"

    def get_type(self):
        return self.__type

    def add_child(self, solid: Solid):
        self.children.append(solid)

    def to_cj(self, vertices):
        return [solid.to_cj(vertices) for solid in self.children]
    
    def get_semantic_surfaces(self):
        semantics = {}
        for solid in self.children:
            for multi_surface in solid.children:
                for surface in multi_surface.children:
                    semantics[surface.semantic['uuid']] = surface.get_semantic_cj()
        return list(semantics.values())
    
    # depth = 3
    def get_semantic_values(self, semantics):
        return [solid.get_semantic_values(semantics) for solid in self.children]

