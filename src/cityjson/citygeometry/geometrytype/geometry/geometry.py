# https://www.cityjson.org/dev/geom-arrays/
from src.uuid import guid

SEMANTIC = {
    # "Building", "BuildingPart", "BuildingRoom", "BuildingStorey", "BuildingUnit", "BuildingInstallation"
    'roof': 'RoofSurface',
    'ground': 'GroundSurface',
    'wall': 'WallSurface',
    'closure': 'ClosureSurface',
    'outer_ceiling': 'OuterCeilingSurface',
    'outer_floor': 'OuterFloorSurface',
    'window': 'Window',
    'door': 'Door',
    'interior_wall': 'InteriorWallSurface',
    'ceiling': 'CeilingSurface',
    'floor': 'FloorSurface',

    # "WaterBody"
    'water': 'WaterSurface',
    'water_ground': 'WaterGroundSurface',
    'water_closure': 'WaterClosureSurface',

    # "Road", "Railway", "TransportSquare"
    'road': 'TrafficArea',
    'auxiliary_road': 'AuxiliaryTrafficArea',
    'marking': 'TransportationMarking',
    'hole': 'TransportationHole',
}


def _get_semantic(name):
    if name in SEMANTIC:
        return SEMANTIC[name]
    if name in SEMANTIC.values():
        return name
    name = name.replace(" ", "")
    if not name.startswith('+'):
        name = '+' + name
    return name


class Primitive:
    def to_cj(self):
        pass

    def get_semantic_surfaces(self):
        pass

    def get_semantic_values(self, semantics):
        pass


class Semantic:
    def __init__(self, name: str):
        self.semantic = {}
        self.semantic['type'] = _get_semantic(name)
        self.add_uuid()

    def __getitem__(self, key):
        return self.semantic[key]
    
    def __setitem__(self, key, value):
        self.semantic[key] = value

    def __eq__(self, other):
        if isinstance(other, Semantic):
            if other['type'] == self.semantic['type']:
                if 'uuid' in other.semantic and 'uuid' in self.semantic:
                    return other['uuid'] == self.semantic['uuid']
                if 'uuid' in other.semantic or 'uuid' in self.semantic:
                    return False
                return True
        return False

    def add_uuid(self, uuid: str = None):
        self.semantic['uuid'] = guid() if uuid is None else uuid

    def to_cj(self):
        return self.semantic


# 3d point
class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def to_cj(self, vertices):
        index = vertices.add(self.x, self.y, self.z)
        return index


# collection of points -> used to create shape
# not a geometry
class MultiPoint:
    __type = "MultiPoint"
    __depth = 1

    def __init__(self, points: list[Point] = []):
        self.points = points

    def add_point(self, point: Point):
        self.points.append(point)

    def to_cj(self):
        return [point.to_cj() for point in self.points]


# This is a surface
# first multi point is the exterior ring
# the rest are interior rings
# not yet a geometry
class MultiLineString:
    __type = "MultiLineString"
    __depth = 2

    def __init__(self, semantic, faces: list[MultiPoint] = []):
        self.semantic = Semantic(semantic)
        self.faces = faces

    def add_face(self, face: MultiPoint):
        self.faces.append(face)

    def set_exterior_face(self, exterior: MultiPoint):
        if len(self.faces) == 0:
            self.faces.append(exterior)
        else:
            self.faces[0] = exterior

    def to_cj(self):
        return [face.to_cj() for face in self.faces]
    
    def get_semantic_cj(self):
        return self.semantic.to_cj()


# Used to create a landscape of a building wall
class MultiSurface(Primitive):
    __type = "MultiSurface" # separate surfaces with holes
    __type_b = "CompositeSurface" # adjacents surfaces without overlap
    __depth = 3

    def __init__(self, surfaces: list[MultiLineString] = []):
        self.surfaces = surfaces

    def add_surface(self, surface: MultiLineString):
        self.surfaces.append(surface)

    def to_cj(self):
        return [surface.to_cj() for surface in self.surfaces]
    
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

    def to_cj(self):
        return [multi_surface.to_cj() for multi_surface in self.multi_surfaces]
    
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
    __type_b = "CompositeSolid" # adjacents solids
    __depth = 5

    def __init__(self, solids: list[Solid] = []):
        self.solids = solids

    def add_solid(self, solid: Solid):
        self.solids.append(solid)

    def to_cj(self):
        return [solid.to_cj() for solid in self.solids]
    
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


class CityGeometry:
    def __init__(self, primitive: Primitive, lod: int = 1):
        self.primitive = primitive

    def to_cj(self):
        semantics = self.primitive.get_semantic_surfaces()
        return {
            'type': self.primitive.__type,
            'lod': self.lod,
            'boundaries': self.primitive.to_cj(),
            'semantics': {
                'surfaces': self.primitive.get_semantic_surfaces(),
                'values': self.primitive.get_semantic_values(semantics)
            }
        }


class CityGemometryParser:
    
