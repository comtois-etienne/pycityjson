from .matrix import TransformationMatrix

from .geometry import (
    CityGeometry,
    Geometry,
    GeometryInstance
)
from .primitive.parser import (
    MultiSolidParser,
    SolidParser,
    MultiSurfaceParser,
    MultiLineStringParser,
    MultiPointParser,
)


ALT_PRIMITIVE = [
    'CompositeSolid',
    'CompositeSurface'
]

GEOMETRY_PARSERS = {
    'CompositeSolid': MultiSolidParser,
    'MultiSolid': MultiSolidParser,
    'Solid': SolidParser,
    'CompositeSurface': MultiSurfaceParser,
    'MultiSurface': MultiSurfaceParser,
    'MultiLineString': MultiLineStringParser,
    'MultiPoint': MultiPointParser,
}



class CityGeometryParser:
    def __init__(self, city):
        self.city = city

    # data contains cityjson['CityObjects'][uuid]['geometry'][index]
    def parse(self, data) -> CityGeometry:
        dtype = data['type']
        if dtype in GEOMETRY_PARSERS:
            parser = GeometryParser(self.city)
            return parser.parse(data)
        elif dtype == 'GeometryInstance':
            parser = InstanceParser(self.city)
            return parser.parse(data)
        else:
            raise ValueError(f'Unknown geometry type: {dtype}')


class GeometryParser:
    def __init__(self, city):
        self.city = city

    # data contains cityjson['CityObjects'][uuid]['geometry'][index]
    def parse(self, data) -> Geometry:
        lod = data['lod']
        dtype = data['type']
        if dtype not in GEOMETRY_PARSERS:
            raise ValueError(f'Unknown geometry type: {dtype}')
        parser = GEOMETRY_PARSERS[dtype](self.city)
        primitive = parser.parse(data)
        if dtype in ALT_PRIMITIVE:
            primitive.type = primitive.__ptype_b
        return Geometry(primitive, lod)


class InstanceParser:
    def __init__(self, city):
        self.city = city
    
    # data contains cityjson['CityObjects'][uuid]['geometry'][index]
    def parse(self, data) -> GeometryInstance:
        origin = self.city[data['boundaries'][0]]
        geometry = self.city.get_geometry_templates()[data['template']]
        matrix = data['transformationMatrix'] # todo extract offset if exists in matrix
        origin = [origin[0] + matrix[3], origin[1] + matrix[7], origin[2] + matrix[11]]
        matrix[3] = 0
        matrix[7] = 0
        matrix[11] = 0
        geometry_instance = GeometryInstance(geometry, TransformationMatrix(matrix))
        geometry_instance.origin = origin
        return geometry_instance


