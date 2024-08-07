# https://www.cityjson.org/dev/geom-arrays/


from .semantic import Semantic


class Primitive:
    def to_cj(self, vertices):
        pass

    def get_semantic_surfaces(self):
        return None

    def get_semantic_values(self, semantics):
        return None


class Point(Primitive):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def to_cj(self, vertices):
        index = vertices.add(self.x, self.y, self.z)
        return index


# collection of points -> used to create shape
class MultiPoint(Primitive):
    __type = "MultiPoint"
    __depth = 1

    def __init__(self, points: list[Point] = []):
        self.points = points

    def add_point(self, point: Point):
        self.points.append(point)

    def to_cj(self, vertices):
        return [point.to_cj(vertices) for point in self.points]


# This is a surface containing the semantic
# first multi point is the exterior ring
# the rest are interior rings
class MultiLineString(Primitive):
    __type = "MultiLineString"
    __depth = 2

    def __init__(self, faces: list[MultiPoint] = [], semantic=None):
        self.semantic = Semantic(semantic)
        self.faces = faces

    def add_face(self, face: MultiPoint):
        self.faces.append(face)

    def set_exterior_face(self, exterior: MultiPoint):
        if len(self.faces) == 0:
            self.faces.append(exterior)
        else:
            self.faces[0] = exterior

    def to_cj(self, vertices):
        return [face.to_cj(vertices) for face in self.faces]
    
    def get_semantic_cj(self):
        return self.semantic.to_cj()


# Used to create a landscape of a building wall
class MultiSurface(Primitive):
    __type = "MultiSurface" # separate surfaces with holes
    __type_a = "MultiSurface" # separate surfaces with holes
    __type_b = "CompositeSurface" # adjacents surfaces without overlap
    __depth = 3

    def __init__(self, surfaces: list[MultiLineString] = []):
        self.surfaces = surfaces

    def add_surface(self, surface: MultiLineString):
        self.surfaces.append(surface)

    def to_cj(self, vertices):
        return [surface.to_cj(vertices) for surface in self.surfaces]
    
    def get_semantic_surfaces(self):
        semantics = {}
        for surface in self.surfaces:
            semantics[surface.semantic['uuid']] = surface.get_semantic_cj()
        return list(semantics.values())

    # depth = 1
    def get_semantic_values(self, semantics):
        semantic_values = []
        for surface in self.surfaces:
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
        self.multi_surfaces = multi_surfaces

    def add_multi_surface(self, multi_surface: MultiSurface):
        self.multi_surfaces.append(multi_surface)

    def to_cj(self, vertices):
        return [multi_surface.to_cj(vertices) for multi_surface in self.multi_surfaces]
    
    def get_semantic_surfaces(self):
        semantics = {}
        for multi_surface in self.multi_surfaces:
            for surface in multi_surface.surfaces:
                semantics[surface.semantic['uuid']] = surface.get_semantic_cj()
        return list(semantics.values())

    # depth = 2
    def get_semantic_values(self, semantics):
        semantic_values = []
        for multi_surface in self.multi_surfaces:
            semantic_values = multi_surface.get_semantic_values(semantics)
            semantic_values.append(semantic_values)
        return semantic_values


class MultiSolid(Primitive):
    __type = "MultiSolid" # separate solids
    __type_a = "MultiSolid" # separate solids
    __type_b = "CompositeSolid" # adjacents solids
    __depth = 5

    def __init__(self, solids: list[Solid] = []):
        self.solids = solids

    def add_solid(self, solid: Solid):
        self.solids.append(solid)

    def to_cj(self, vertices):
        return [solid.to_cj(vertices) for solid in self.solids]
    
    def get_semantic_surfaces(self):
        semantics = {}
        for solid in self.solids:
            for multi_surface in solid.multi_surfaces:
                for surface in multi_surface.surfaces:
                    semantics[surface.semantic['uuid']] = surface.get_semantic_cj()
        return list(semantics.values())
    
    # depth = 3
    def get_semantic_values(self, semantics):
        semantic_values = []
        for solid in self.solids:
            semantic_values = solid.get_semantic_values(semantics)
            semantic_values.append(semantic_values)
        return semantic_values

