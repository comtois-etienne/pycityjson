import numpy as np

from src.cityjson import City, CityObjects, CityObject, TransformationMatrix, Vertices
from src.cityjson.geometry import GeometryPrimitive, GeometryInstance, CityGeometry
from src.cityjson.template import GeometryTemplates

from src.cityjson.primitive import (
    Semantic,
    Primitive,
    Point,
    MultiPoint,
    MultiLineString,
    MultiSurface,
    Solid,
    MultiSolid
)


def get_attribute(data, key, *, default=None):
    if key in data:
        return data[key]
    return default

def get_nested_attribute(data, key_a, key_b, *, default=None):
    if key_a in data and key_b in data[key_a]:
        return data[key_a][key_b]
    return default


class SemanticParser:
    def __init__(self, city):
        self.city = city

    def parse(self, data) -> list[Semantic]:
        semantics = []
        for s in data:
            semantic = Semantic(s['type'])
            for key, value in s.items():
                semantic[key] = value
            semantics.append(semantic)
        return semantics


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


class GeometryTemplateParser:
    def __init__(self, city):
        self.city = city

    # data contains cityjson['geometry-templates']
    def parse(self, data) -> GeometryTemplates:
        city = City()
        v_parser = VerticesParser([0, 0, 0], [1.0, 1.0, 1.0], self.city.precision())
        city.vertices = v_parser.parse(get_attribute(data, 'vertices-templates', default=[]))
        
        gm_parser = GeometryParser(city)
        templates_data = get_attribute(data, 'templates', default=[])
        templates = [gm_parser.parse(template) for template in templates_data]

        return GeometryTemplates(templates, city.vertices)


class CityObjectParser:
    def __init__(self, city: City):
        self.city = city
        self.geometry_parser = CityGeometryParser(self.city)

    def _link_children(self, city_object, city_objects):
        children_uuids = city_object.children
        city_object.children = []
        for child_uuid in children_uuids:
            child = city_objects.get_by_uuid(child_uuid)
            city_object.add_child(child) if child is not None else None

    def _link_parents(self, city_object, city_objects):
        parents_uuids = city_object.parents
        city_object.parents = []
        for parent_uuid in parents_uuids:
            parent = city_objects.get_by_uuid(parent_uuid)
            city_object.add_parent(parent) if parent is not None else None

    # data contains cityjson['CityObjects'][uuid]
    def parse(self, uuid, data) -> CityObject:
        geometry = [self.geometry_parser.parse(g) for g in get_attribute(data, 'geometry', default=[])]

        city_object = CityObject(
            cityobjects = self.city.cityobjects,
            type = get_attribute(data, 'type', default='GenericCityObject'),
            attributes = get_attribute(data, 'attributes', default={}),
            geometries = geometry,
            children = get_attribute(data, 'children', default=[]),
            parents = get_attribute(data, 'parents', default=None)
        )

        city_object.geo_extent = get_attribute(data, 'geographicalExtent', default=None)
        city_object.set_attribute('uuid', uuid)
        if city_object.type == 'CityObjectGroup':
            city_object = city_object.to_citygroup(get_attribute(data, 'children_roles', default=[]))
        return city_object


class CityObjectsParser:
    def __init__(self, city):
        self.city = city

    # data contains cityjson['CityObjects']
    def parse(self, data) -> CityObjects:
        city_objects = CityObjects()
        parser = CityObjectParser(self.city)

        for uuid, data in data.items():
            cityobject = parser.parse(uuid, data)
            city_objects.add_cityobject(cityobject)

        for city_object in city_objects:
            parser._link_parents(city_object, city_objects)
            parser._link_children(city_object, city_objects)

        return city_objects


class VerticesParser:
    def __init__(self, origin, scale, precision):
        self.translate = origin
        self.scale = scale
        self.precision = precision

    # data contains cityjson['vertices']
    def parse(self, data):
        if len(data) == 0:
            return Vertices()
        vertices = np.array(data)
        vertices = (vertices * np.array(self.scale)) + np.array(self.translate)
        if self.precision is not None:
            vertices = np.round(vertices, self.precision)
        vertices = vertices.tolist()
        return Vertices(vertices)


class CityParser:
    def __init__(self, cityjson):
        self.data = cityjson
        self.city = City()

    # data contains cityjson
    def parse(self):
        self.city.type = get_attribute(self.data, 'type', default='CityJSON')
        self.city.version = get_attribute(self.data, 'version', default='2.0')
        self.city.metadata = get_attribute(self.data, 'metadata', default={})
        self.city.scale = get_nested_attribute(self.data, 'transform', 'scale', default=[0.001, 0.001, 0.001])
        self.city.origin = get_nested_attribute(self.data, 'transform', 'translate', default=[0, 0, 0])

        v_parser = VerticesParser(self.city.origin, self.city.scale, self.city.precision())
        self.city.vertices = v_parser.parse(get_attribute(self.data, 'vertices', default=[]))

        gt_parser = GeometryTemplateParser(self.city)
        self.city.geometry_templates = gt_parser.parse(get_attribute(self.data, 'geometry-templates', default={}))

        co_parser = CityObjectsParser(self.city)
        self.city.cityobjects = co_parser.parse(get_attribute(self.data, 'CityObjects', default=[]))

    def get_city(self) -> City:
        return self.city

