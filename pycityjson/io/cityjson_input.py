import numpy as np

from pycityjson.model import (
    City,
    CityGeometry,
    CityObject,
    CityObjects,
    GeometryInstance,
    GeometryPrimitive,
    GeometryTemplates,
    MultiLineString,
    MultiPoint,
    MultiSolid,
    MultiSurface,
    Point,
    Primitive,
    Semantic,
    Solid,
    TransformationMatrix,
    Vertices,
)


def get_attribute(data: dict, key: str, *, default=None):
    """
    :param data: dictionary to search for the key
    :param key: key to search in the dictionary
    :param default: default value to return if the key is not found
    """
    if key in data:
        return data[key]
    return default


def get_nested_attribute(data: dict, key_a: str, key_b: str, *, default=None):
    """
    :param data: dictionary to search for the key
    :param key_a: first level key to search in the dictionary
    :param key_b: second level key to search in the dictionary
    """
    if key_a in data and key_b in data[key_a]:
        return data[key_a][key_b]
    return default


class SemanticParser:
    def __init__(self, city: City):
        self.city: City = city

    def parse(self, data: list[dict]) -> list[Semantic]:
        """
        :param data: list of raw semantics data. each element is a dictionary with at least a 'type' key
        """
        semantics = []
        for s in data:
            semantic = Semantic(s['type'])
            for key, value in s.items():
                semantic[key] = value
            semantics.append(semantic)
        return semantics


class PrimitiveParser:
    def __init__(self, city: City):
        self.city: City = city

    def _parse(self, primitive_class: 'PrimitiveParser', child_parser_class: 'PrimitiveParser', boundary: list, semantics: list=None, values: list=None) -> Primitive:
        """
        Used to parse the children of the primitive

        :param primitive_class: class of the primitive to create
        :param child_parser_class: parser class of the children of the primitive
        :param boundary: list of the boundary indexes of the primitive
        :param semantics: list of the semantics of the primitive
        :param values: list of the indexes of the semantics for each MultiLineString
        """
        primitive = primitive_class(semantic=semantics[values]) if isinstance(values, int) else primitive_class()

        child_parser = child_parser_class(self.city)
        for i, child in enumerate(boundary):
            value = None if values is None or isinstance(values, int) else values[i]
            child = child_parser._parse(child, semantics, value)
            primitive.add_child(child)

        return primitive

    def parse(self, data: dict) -> Primitive:
        """
        Used to parse with the correct primitive parser
        data contains cityjson['CityObjects'][uuid]['geometry'][index]

        :param data: dictionary containing the geometry data at a specific index
        """
        semantics_surface = get_nested_attribute(data, 'semantics', 'surfaces', default=None)
        semantics_values = get_nested_attribute(data, 'semantics', 'values', default=None)
        semantics = SemanticParser(self.city).parse(semantics_surface) if semantics_surface is not None else None
        boundaries = data['boundaries']
        return self._parse(boundaries, semantics, semantics_values)


class PointParser(PrimitiveParser):
    __primitive = Point
    __child_parser = None

    def _parse(self, boundary: int, semantics=None, values=None) -> Point:
        """
        :param boundary: index of the point in the vertices
        :param semantics: not used
        :param values: not used
        """
        point = self.city[boundary]
        return self.__primitive(point[0], point[1], point[2])

    def parse(self, data: int) -> Point:
        """
        used to override the parent method only
        data contains the index of the point in the vertices
        :param data: index of the point in the vertices
        """
        return self._parse(data)


class MultiPointParser(PrimitiveParser):
    __primitive = MultiPoint
    __child_parser = PointParser

    def _parse(self, boundary: list[int], semantics=None, values=None) -> MultiPoint:
        """
        Used when a child of a MultiLineString
        :param boundary: list of the indexes of the points in the vertices
        :param semantics: not used
        :param values: not used
        """
        return super()._parse(self.__primitive, self.__child_parser, boundary, semantics, values)

    def parse(self, data: dict) -> MultiPoint:
        """
        Used when the geometry in the CityObject is a MultiPoint
        It cannot have semantics
        :param data: dict containing the geometry data (see PrimitiveParser.parse)
        """
        boundaries = data['boundaries']
        return self._parse(boundaries)


# contains the semantic IF a child
class MultiLineStringParser(PrimitiveParser):
    __primitive = MultiLineString
    __child_parser = MultiPointParser

    def _parse(self, boundary: list[list[int]], semantics: list[dict]=None, values: int=None) -> MultiLineString:
        """
        Use when a child of a MultiSurface
        :param boundary: list of raw MultiPoint primitives
        :param semantics: list of the semantics of the primitive
        :param values: the index of the semantics for the MultiLineString
        """
        return super()._parse(self.__primitive, self.__child_parser, boundary, semantics, values)

    def parse(self, data: dict) -> MultiLineString:
        """
        Used when the geometry in the CityObject is a MultiLineString
        It cannot have semantics when at the top level of the geometry
        :param data: dict containing the geometry data (see PrimitiveParser.parse)
        """
        boundaries = data['boundaries']
        return self._parse(boundaries)


class MultiSurfaceParser(PrimitiveParser):
    __primitive = MultiSurface
    __child_parser = MultiLineStringParser

    def _parse(self, boundary: list[list[list[int]]], semantics: list[dict], values: list[int]) -> MultiSurface:
        """
        Used when a child of a Solid
        :param boundary: list of raw MultiLineString primitives
        :param semantics: list of the semantics of the primitive
        :param values: list of the indexes of the semantics for each MultiLineString
        """
        return super()._parse(self.__primitive, self.__child_parser, boundary, semantics, values)


class SolidParser(PrimitiveParser):
    __primitive = Solid
    __child_parser = MultiSurfaceParser

    def _parse(self, boundary: list[list[list[list[int]]]], semantics: list[dict], values: list[list[int]]) -> Solid:
        """
        Used when a child of a MultiSolid
        :param boundary: list of raw MultiSurface primitives
        :param semantics: list of the semantics of the primitive
        :param values: list the semantics for each MultiSurface
        """
        return super()._parse(self.__primitive, self.__child_parser, boundary, semantics, values)


class MultiSolidParser(PrimitiveParser):
    __primitive = MultiSolid
    __child_parser = SolidParser

    def _parse(self, boundary: list[list[list[list[list[int]]]]], semantics: list[dict], values: list[list[list[int]]]) -> MultiSolid:
        """
        :param boundary: list of raw Solid primitives
        :param semantics: list of the semantics of the primitive
        :param values: list of the semantics for each Solid
        """
        return super()._parse(self.__primitive, self.__child_parser, boundary, semantics, values)


ALT_PRIMITIVE = ['CompositeSolid', 'CompositeSurface']

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
            cityobjects=self.city.cityobjects,
            type=get_attribute(data, 'type', default='GenericCityObject'),
            attributes=get_attribute(data, 'attributes', default={}),
            geometries=geometry,
            children=get_attribute(data, 'children', default=[]),
            parents=get_attribute(data, 'parents', default=None),
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
        self.__translate = origin
        self.__scale = scale
        self.__precision = precision

    # data contains cityjson['vertices']
    def parse(self, data):
        if len(data) == 0:
            return Vertices(precision=self.__precision)

        vertices = np.array(data)
        vertices = (vertices * np.array(self.__scale)) + np.array(self.__translate)

        if self.__precision is not None:
            vertices = np.round(vertices, self.__precision)

        vertices = vertices.tolist()

        return Vertices(vertices, precision=self.__precision)


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
