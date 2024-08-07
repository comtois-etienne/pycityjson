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
    if name is None:
        return None
    if name in SEMANTIC:
        return SEMANTIC[name]
    if name in SEMANTIC.values():
        return name
    name = name.replace(" ", "")
    if not name.startswith('+'):
        name = '+' + name
    return name


class Primitive:
    def to_cj(self, vertices):
        pass

    def get_semantic_surfaces(self):
        return None

    def get_semantic_values(self, semantics):
        return None


class Semantic:
    def __init__(self, dtype: str):
        self.semantic = {}
        self.semantic['type'] = _get_semantic(dtype)
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


class SemanticsParser:
    def __init__(self, cityjson):
        self.cityjson = cityjson

    def parse(self, data) -> list[Semantic]:
        semantics = []
        for s in data:
            semantic = Semantic(s['type'])
            for key, value in s.items():
                semantic[key] = value
            semantics.append(semantic)
        return semantics


class Point:
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



# BEGIN GEOMETRY

class CityGeometry:
    def to_cj(self, vertices):
        pass


# Primitive
class CityPrimitive(CityGeometry):
    def __init__(self, primitive: Primitive, lod: str = '1'):
        self.primitive = primitive
        self.lod = lod

    def to_cj(self, vertices):
        citygeometry = {
            'type': self.primitive.__type,
            'lod': self.lod,
            'boundaries': self.primitive.to_cj(vertices)
        }
        semantics = self.primitive.get_semantic_surfaces()
        if semantics is not None and semantics[0]['type'] is not None:
            citygeometry['semantics'] = {
                'surfaces': semantics,
                'values': self.primitive.get_semantic_values(semantics)
            }
        return citygeometry


# Template
class CityInstance(CityGeometry):
    #todo
    pass


# END GEOMETRY


# BEGIN PARSER

class PrimitiveParser:
    def __init__(self, cityjson):
        self.cityjson = cityjson

    def parse(self, data) -> Primitive:
        pass

    def _parse(self, boundary, semantics, values):
        pass


class MultiPointParser(PrimitiveParser):
    def parse(self, data) -> MultiPoint:
        points = []
        for index in data['boundaries']:
            point = self.cityjson[index]
            points.append(Point(point[0], point[1], point[2]))
        return MultiPoint(points)
    
    def _parse(self, boundary, semantics, values):
        pass


class MultiLineStringParser(PrimitiveParser):
    __child_parser = MultiPointParser

    def parse(self, data) -> MultiLineString:
        boundaries = data['boundaries']
        multi_points = []
        for i, multi_point in enumerate(boundaries):
            multi_points.append(
                MultiPointParser(self.cityjson).parse(multi_point)
            )
        return MultiLineString(multi_points) # receives the final semantic

    def _parse(self, boundary, semantics, values):
        multi_points = []
        for i, multi_point in enumerate(boundary):
            multi_points.append(
                MultiPointParser(self.cityjson)._parse(multi_point)
            )
        return MultiLineString(multi_points, semantics[values])


class MultiSurfaceParser(PrimitiveParser):
    def parse(self, data) -> MultiSurface:
        semantics = SemanticsParser(self.cityjson).parse(data['semantics']['surfaces'])
        values = data['semantics']['values']
        boundaries = data['boundaries']
        multi_lines = []
        for i, multi_line in enumerate(boundaries):
            multi_lines.append(
                MultiLineStringParser(self.cityjson)._parse(
                    multi_line, semantics, values[i]
                )
            )
        return MultiSurface(multi_lines)

    def _parse(self, boundary, semantics, values):
        multi_lines = []
        for i, multi_line in enumerate(boundary):
            multi_lines.append(
                MultiLineStringParser(self.cityjson)._parse(
                    multi_line, semantics, values[i]
                )
            )
        return MultiSurface(multi_lines)


class SolidParser(PrimitiveParser):
    __child_parser = MultiSurfaceParser

    def parse(self, data) -> Solid:
        semantics = SemanticsParser(self.cityjson).parse(data['semantics']['surfaces'])
        values = data['semantics']['values']
        boundaries = data['boundaries']
        multi_surfaces = []
        for i, multi_surface in enumerate(boundaries):
            multi_surfaces.append(
                MultiSurfaceParser(self.cityjson)._parse(
                    multi_surface, semantics, values[i]
                )
            )
        return Solid(multi_surfaces)

    def _parse(self, boundary, semantics, values):
        multi_surfaces = []
        for i, multi_surface in enumerate(boundary):
            multi_surfaces.append(
                MultiSurfaceParser(self.cityjson)._parse(
                    multi_surface, semantics, values[i]
                )
            )
        return Solid(multi_surfaces)


def _parse(primitive: Primitive, child_parser: PrimitiveParser, cityjson, data):
    semantics = SemanticsParser(cityjson).parse(data['semantics']['surfaces'])
    values = data['semantics']['values']
    boundaries = data['boundaries']
    children = []

    if isinstance(values, list):
        for i, child in enumerate(boundaries):
            children.append(
                child_parser(cityjson)._parse(
                    child, semantics, values[i]
                )
            )
    else:
        for i, child in enumerate(boundaries):
            children.append(child_parser(cityjson).parse(child), semantics[values])
    return primitive(children)


class MultiSolidParser(PrimitiveParser):
    __child_parser = SolidParser

    def parse(self, data) -> MultiSolid:
        semantics = SemanticsParser(self.cityjson).parse(data['semantics']['surfaces'])
        values = data['semantics']['values']
        boundaries = data['boundaries']
        solids = []
        for i, solid in enumerate(boundaries):
            solids.append(
                SolidParser(self.cityjson)._parse(
                    solid, semantics, values[i]
                )
            )
        return MultiSolid(solids)


class CityInstanceParser:
    #todo
    pass


class CityGemometryParser:
    def __init__(self, cityjson):
        self.cityjson = cityjson

    # data contains cityobject['geometry'][i]
    def parse(self, data) -> CityGeometry:
        dtype = data['type']
        lod = data['lod']
        primitive = None

        if dtype == 'GeometryInstance':
            pass
        elif dtype == 'CompositeSolid':
            primitive = MultiSolidParser(self.cityjson).parse(data)
            primitive.__type = primitive.__type_b
        elif dtype == 'MultiSolid':
            primitive = MultiSolidParser(self.cityjson).parse(data)
        elif dtype == 'Solid':
            primitive = SolidParser(self.cityjson).parse(data)
        elif dtype == 'MultiSurface':
            primitive = MultiSurfaceParser(self.cityjson).parse(data)
        elif dtype == 'CompositeSurface':
            primitive = MultiSurfaceParser(self.cityjson).parse(data)
            primitive.__type = primitive.__type_b
        else:
            print("Geometry type not implemented yet")

        return CityPrimitive(primitive, lod)

