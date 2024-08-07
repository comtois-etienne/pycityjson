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
    __primitive = None
    __child_parser = None

    def __init__(self, city):
        self.city = city

    def _parse(self, boundary, semantics=None, values=None) -> Primitive:
        children = []
        for i, child in enumerate(boundary):
            value = values[i] if values is not None else None
            children.append(
                self.__child_parser(self.city)._parse(
                    child, semantics, value
                )
            )
        # MultiLineString if a child
        if values is not None and isinstance(values, int):
            return self.__primitive(children, semantics[values])
        return self.__primitive(children)

    def parse(self, data) -> Primitive:
        semantics = SemanticParser(self.city).parse(data['semantics']['surfaces'])
        values = data['semantics']['values']
        boundaries = data['boundaries']
        # MuliSolid, Solid, MultiSurface
        return self._parse(boundaries, semantics, values)


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

    # def _parse(self, boundary, semantics=None, values=None):
    #     return super()._parse(boundary, semantics, values)

    def parse(self, data) -> MultiPoint:
        boundaries = data['boundaries']
        return self._parse(boundaries)


# contains the semantic IF a child
class MultiLineStringParser(PrimitiveParser):
    __primitive = MultiLineString
    __child_parser = MultiPointParser

    # def _parse(self, boundary, semantics=None, values=None):
    #     super()._parse(boundary, semantics, values)

    # no semantics
    def parse(self, data) -> Primitive:
        boundaries = data['boundaries']
        return self._parse(boundaries)


class MultiSurfaceParser(PrimitiveParser):
    __primitive = MultiSurface
    __child_parser = MultiLineStringParser

    # def _parse(self, boundary, semantics, values):
    #     return super()._parse(boundary, semantics, values)

    # def parse(self, data) -> Primitive:
    #     return super().parse(data)


class SolidParser(PrimitiveParser):
    __primitive = Solid
    __child_parser = MultiSurfaceParser

    # def _parse(self, boundary, semantics, values):
    #     return super()._parse(boundary, semantics, values)
    
    # def parse(self, data) -> Primitive:
    #     return super().parse(data)


class MultiSolidParser(PrimitiveParser):
    __primitive = MultiSolid
    __child_parser = SolidParser

    # def _parse(self, boundary, semantics, values):
    #     return super()._parse(boundary, semantics, values)

    # def parse(self, data) -> Primitive:
    #     return super().parse(data)

