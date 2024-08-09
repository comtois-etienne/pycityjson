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
        index = vertices.add(self.x, self.y, self.z)
        return index


# collection of points -> used to create shape
class MultiPoint(Primitive):
    __type = "MultiPoint"
    __depth = 1

    def __init__(self, points: list[Point] = []):
        self.children = points

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

    def __init__(self, faces: list[MultiPoint] = [], semantic=None):
        self.semantic = semantic
        self.children = faces

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


# Used to create a landscape of a building wall
class MultiSurface(Primitive):
    __type = "MultiSurface" # separate surfaces with holes
    __type_a = "MultiSurface" # separate surfaces with holes
    __type_b = "CompositeSurface" # adjacents surfaces without overlap
    __depth = 3

    def __init__(self, surfaces: list[MultiLineString] = []):
        self.children = surfaces

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
        semantic_values = []
        for surface in self.children:
            uuid = surface.semantic['uuid']
            for i, semantic in enumerate(semantics):
                if semantic == uuid:
                    semantic_values.append(i)
                    break
        return semantic_values


# Used to create a building
class Solid(Primitive):
    __type = "Solid"
    __depth = 4

    def __init__(self, multi_surfaces: list[MultiSurface] = []):
        self.children = multi_surfaces

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
        semantic_values = []
        for multi_surface in self.children:
            semantic_values = multi_surface.get_semantic_values(semantics)
            semantic_values.append(semantic_values)
        return semantic_values


class MultiSolid(Primitive):
    __type = "MultiSolid" # separate solids
    __type_a = "MultiSolid" # separate solids
    __type_b = "CompositeSolid" # adjacents solids
    __depth = 5

    def __init__(self, solids: list[Solid] = []):
        self.children = solids

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
        semantic_values = []
        for solid in self.children:
            semantic_values = solid.get_semantic_values(semantics)
            semantic_values.append(semantic_values)
        return semantic_values

