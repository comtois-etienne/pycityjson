from .matrix import TransformationMatrix

from .geometry import (
    CityGeometry,
    GeometryPrimitive,
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
    def parse(self, data) -> GeometryPrimitive:
        lod = data['lod']
        dtype = data['type']
        if dtype not in GEOMETRY_PARSERS:
            raise ValueError(f'Unknown geometry type: {dtype}')
        parser = GEOMETRY_PARSERS[dtype](self.city)
        primitive = parser.parse(data)
        if dtype in ALT_PRIMITIVE:
            primitive.type = primitive.__ptype_b
        return GeometryPrimitive(primitive, lod)


class InstanceParser:
    def __init__(self, city):
        self.city = city
    
    # data contains cityjson['CityObjects'][uuid]['geometry'][index]
    def parse(self, data) -> GeometryInstance:
        origin = self.city[data['boundaries'][0]]
        geometry = self.city.get_geometry_templates()[data['template']]
        matrix = data['transformationMatrix']
        matrix = TransformationMatrix(matrix)
        matrix = matrix.move(origin)
        return GeometryInstance(geometry, matrix)

