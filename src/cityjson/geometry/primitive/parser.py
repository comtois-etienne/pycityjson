from src.scripts.attribute import get_nested_attribute
from .semantic import SemanticParser
from .primitive import (
    Primitive,
    Point,
    MultiPoint,
    MultiLineString,
    MultiSurface,
    Solid,
    MultiSolid
)


class PrimitiveParser:
    def __init__(self, city):
        self.city = city

    # parsing children
    def _parse(self, primitive_class, child_parser_class, boundary, semantics=None, values=None) -> Primitive:
        primitive = primitive_class(semantic = semantics[values]) if isinstance(values, int) else primitive_class()

        child_parser = child_parser_class(self.city)
        for i, child in enumerate(boundary):
            value = None if values is None or isinstance(values, int) else values[i]
            child = child_parser._parse(child, semantics, value)
            primitive.add_child(child)
        
        return primitive

    # data contains cityjson['CityObjects'][uuid]['geometry'][index]
    def parse(self, data) -> Primitive:
        semantics_surface = get_nested_attribute(data, 'semantics', 'surfaces', default=None)
        semantics_values = get_nested_attribute(data, 'semantics', 'values', default=None)
        semantics = SemanticParser(self.city).parse(semantics_surface) if semantics_surface is not None else None
        boundaries = data['boundaries']
        return self._parse(boundaries, semantics, semantics_values)


class PointParser(PrimitiveParser):
    __primitive = Point
    __child_parser = None

    def _parse(self, boundary, semantics=None, values=None):
        point = self.city[boundary]
        return self.__primitive(point[0], point[1], point[2])

    def parse(self, data) -> Point:
        return self._parse(data)


class MultiPointParser(PrimitiveParser):
    __primitive = MultiPoint
    __child_parser = PointParser

    def _parse(self, boundary, semantics=None, values=None):
        return super()._parse(
            self.__primitive, 
            self.__child_parser, 
            boundary, semantics, values
        )

    def parse(self, data) -> MultiPoint:
        boundaries = data['boundaries']
        return self._parse(boundaries)


# contains the semantic IF a child
class MultiLineStringParser(PrimitiveParser):
    __primitive = MultiLineString
    __child_parser = MultiPointParser

    def _parse(self, boundary, semantics=None, values=None):
        return super()._parse(
            self.__primitive, 
            self.__child_parser, 
            boundary, semantics, values
        )

    # no semantics
    def parse(self, data) -> Primitive:
        boundaries = data['boundaries']
        return self._parse(boundaries)


class MultiSurfaceParser(PrimitiveParser):
    __primitive = MultiSurface
    __child_parser = MultiLineStringParser

    def _parse(self, boundary, semantics, values):
        return super()._parse(
            self.__primitive, 
            self.__child_parser, 
            boundary, semantics, values
        )

    def parse(self, data) -> Primitive:
        return super().parse(data)


class SolidParser(PrimitiveParser):
    __primitive = Solid
    __child_parser = MultiSurfaceParser

    def _parse(self, boundary, semantics, values):
        return super()._parse(
            self.__primitive, 
            self.__child_parser, 
            boundary, semantics, values
        )
    
    def parse(self, data) -> Primitive:
        return super().parse(data)


class MultiSolidParser(PrimitiveParser):
    __primitive = MultiSolid
    __child_parser = SolidParser

    def _parse(self, boundary, semantics, values):
        return super()._parse(
            self.__primitive, 
            self.__child_parser, 
            boundary, semantics, values
        )

    def parse(self, data) -> Primitive:
        return super().parse(data)

