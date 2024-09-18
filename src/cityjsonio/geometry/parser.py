from src.cityjson import City, TransformationMatrix

from src.cityjson.geometry import (
    CityGeometry,
    GeometryPrimitive,
    GeometryInstance
)
from .primitive import (
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
    def __init__(self, city: City):
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
    def __init__(self, city: City):
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
            primitive.type = dtype
        return GeometryPrimitive(primitive, lod)


class InstanceParser:
    def __init__(self, city: City):
        self.city = city
    
    # data contains cityjson['CityObjects'][uuid]['geometry'][index]
    def parse(self, data) -> GeometryInstance:
        origin = self.city[data['boundaries'][0]]
        geometry = self.city.geometry_templates[data['template']]
        matrix = data['transformationMatrix']
        matrix = TransformationMatrix(matrix)
        matrix = matrix.translate(origin)
        return GeometryInstance(geometry, matrix)

