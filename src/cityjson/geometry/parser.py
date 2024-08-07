from .primitive import CityPrimitive
from .geometry import CityGeometry
from .primitive.parser import (
    MultiSolidParser,
    SolidParser,
    MultiSurfaceParser,
    MultiLineStringParser,
    MultiPointParser,
)


class InstanceParser:
    #todo
    pass


class CityGeometryParser:
    def __init__(self, city):
        self.city = city

    # data contains cityjson['CityObjects'][uuid]['geometry'][index]
    def parse(self, data) -> CityGeometry:
        dtype = data['type']
        lod = data['lod']
        primitive = None

        alt_primitive = [
            'CompositeSolid',
            'CompositeSurface'
        ]

        parsers = {
            'GeometryInstance': InstanceParser, #todo
            'CompositeSolid': MultiSolidParser,
            'MultiSolid': MultiSolidParser,
            'Solid': SolidParser,
            'CompositeSurface': MultiSurfaceParser,
            'MultiSurface': MultiSurfaceParser,
            'MultiLineString': MultiLineStringParser,
            'MultiPoint': MultiPointParser,
        }

        if dtype in parsers:
            primitive = parsers[dtype](self.city).parse(data)
        if dtype in alt_primitive:
            primitive.__type = primitive.__type_b

        return CityPrimitive(primitive, lod)

