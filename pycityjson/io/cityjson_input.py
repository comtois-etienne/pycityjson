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
    Vertex,
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

    def _parse(self, primitive_class: 'PrimitiveParser', child_parser_class: 'PrimitiveParser', boundary: list, semantics: list = None, values: list = None) -> Primitive:
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

    def _parse(self, boundary: list[list[int]], semantics: list[dict] = None, values: int = None) -> MultiLineString:
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
        self.__city: City = city

    def parse(self, data: dict) -> CityGeometry:
        """
        data contains cityjson['CityObjects'][uuid]['geometry'][index]
        will parse with the correct parser (PrimitiveParser or InstanceParser)
        :param data: dict containing one geometry data
        """
        dtype = data['type']
        if dtype in GEOMETRY_PARSERS:
            parser = GeometryParser(self.__city)
            return parser.parse(data)
        elif dtype == 'GeometryInstance':
            parser = InstanceParser(self.__city)
            return parser.parse(data)
        else:
            raise ValueError(f'Unknown geometry type: {dtype}')


class GeometryParser:
    def __init__(self, city: City):
        self.__city: City = city

    def parse(self, data: dict) -> GeometryPrimitive:
        """
        data contains cityjson['CityObjects'][uuid]['geometry'][index]
        :param data: dict containing one geometry data of type Primitive
        """
        lod = data['lod']
        dtype = data['type']
        if dtype not in GEOMETRY_PARSERS:
            raise ValueError(f'Unknown geometry type: {dtype}')
        parser = GEOMETRY_PARSERS[dtype](self.__city)
        primitive = parser.parse(data)
        if dtype in ALT_PRIMITIVE:
            primitive.type = dtype
        return GeometryPrimitive(primitive, lod)


class InstanceParser:
    def __init__(self, city: City):
        self.__city: City = city

    def parse(self, data: dict) -> GeometryInstance:
        """
        data contains cityjson['CityObjects'][uuid]['geometry'][index]
        :param data: dict containing one geometry data of type Instance
        """
        origin = self.__city[data['boundaries'][0]]
        geometry = self.__city.geometry_templates[data['template']]
        matrix = data['transformationMatrix']
        matrix = TransformationMatrix(matrix)
        matrix = matrix.translate(origin)
        return GeometryInstance(geometry, matrix)


class GeometryTemplateParser:
    def __init__(self, city):
        self.__city: City = city

    def parse(self, data: dict) -> GeometryTemplates:
        """
        data contains cityjson['geometry-templates']
        must have the keys 'vertices-templates' and 'templates' in the dictionary
        :param data: dict containing all the geometry templates
        """
        city = City()  # create a new city to avoid modifying the original city
        v_parser = VerticesParser([0, 0, 0], [1.0, 1.0, 1.0], self.__city.precision())
        city.vertices = v_parser.parse(get_attribute(data, 'vertices-templates', default=[]))

        gm_parser = GeometryParser(city)
        templates_data = get_attribute(data, 'templates', default=[])
        templates = [gm_parser.parse(template) for template in templates_data]

        return GeometryTemplates(templates, city.vertices)


class CityObjectParser:
    def __init__(self, city: City):
        self.__city: City = city
        self.__geometry_parser = CityGeometryParser(self.__city)

    def _link_children(self, city_object: CityObject, city_objects: CityObjects):
        """
        All the cityobjects need to be parsed before linking the children
        :param city_object: CityObject to link the children
        :param city_objects: CityObjects containing all the CityObject
        """
        children_uuids = city_object.children
        city_object.children = []
        for child_uuid in children_uuids:
            child = city_objects.get_by_uuid(child_uuid)
            city_object.add_child(child) if child is not None else None

    def _link_parents(self, city_object: CityObject, city_objects: CityObjects):
        """
        All the cityobjects need to be parsed before linking the parents
        :param city_object: CityObject to link the parents
        :param city_objects: CityObjects containing all the CityObject
        """
        parents_uuids = city_object.parents
        city_object.parents = []
        for parent_uuid in parents_uuids:
            parent = city_objects.get_by_uuid(parent_uuid)
            city_object.add_parent(parent) if parent is not None else None

    def parse(self, uuid: str, data: dict) -> CityObject:
        """
        data contains cityjson['CityObjects'][uuid]
        :param uuid: uuid of the CityObject
        :param data: dict containing the CityObject attributes and geometries
        """
        geometry: list[CityGeometry] = [self.__geometry_parser.parse(g) for g in get_attribute(data, 'geometry', default=[])]

        city_object = CityObject(
            cityobjects=self.__city.cityobjects,
            type=get_attribute(data, 'type', default='GenericCityObject'),
            attributes=get_attribute(data, 'attributes', default={}),
            geometries=geometry,
            children=get_attribute(data, 'children', default=[]),
            parents=get_attribute(data, 'parents', default=None),
        )

        city_object.geo_extent = get_attribute(data, 'geographicalExtent', default=None)
        city_object.set_attribute('uuid', uuid)
        if city_object.type == 'CityObjectGroup':
            city_object = city_object.to_cityobjectgroup(get_attribute(data, 'children_roles', default=[]))
        return city_object


class CityObjectsParser:
    def __init__(self, city: City):
        self.__city: City = city

    def parse(self, data: dict) -> CityObjects:
        """
        data contains cityjson['CityObjects']
        :param data: dict containing all the CityObjects. the keys are the uuid of the CityObject
        """
        city_objects = CityObjects()
        parser = CityObjectParser(self.__city)

        for uuid, data in data.items():
            cityobject = parser.parse(uuid, data)
            city_objects.add_cityobject(cityobject)

        # to be called after all the cityobjects are parsed
        for city_object in city_objects:
            parser._link_parents(city_object, city_objects)
            parser._link_children(city_object, city_objects)

        return city_objects


class VerticesParser:
    def __init__(self, origin: Vertex, scale: Vertex, precision: int = None):
        self.__translate: Vertex = origin
        self.__scale: Vertex = scale
        self.__precision: int | None = precision

    def parse(self, data: list[Vertex]) -> Vertices:
        """
        data contains cityjson['vertices']
        :param data: list of vertices in x, y, z format
        """
        if len(data) == 0:
            return Vertices(precision=self.__precision)
        else:
            vertices = (np.array(data) * np.array(self.__scale)) + np.array(self.__translate)
            if self.__precision is not None:
                vertices = np.round(vertices, self.__precision)
            return Vertices(vertices.tolist(), precision=self.__precision)


class CityParser:
    def __init__(self, cityjson: dict):
        """
        :param cityjson: dictionary containing the whole cityjson data
        """
        self.__data: dict = cityjson
        self.__city: City = City()

    def parse(self):
        self.__city.type = get_attribute(self.__data, 'type', default='CityJSON')
        self.__city.version = get_attribute(self.__data, 'version', default='2.0')
        self.__city.metadata = get_attribute(self.__data, 'metadata', default={})
        self.__city.scale = get_nested_attribute(self.__data, 'transform', 'scale', default=[0.001, 0.001, 0.001])
        self.__city.origin = get_nested_attribute(self.__data, 'transform', 'translate', default=[0, 0, 0])

        v_parser = VerticesParser(self.__city.origin, self.__city.scale, self.__city.precision())
        self.__city.vertices = v_parser.parse(get_attribute(self.__data, 'vertices', default=[]))

        gt_parser = GeometryTemplateParser(self.__city)
        self.__city.geometry_templates = gt_parser.parse(get_attribute(self.__data, 'geometry-templates', default={}))

        co_parser = CityObjectsParser(self.__city)
        self.__city.cityobjects = co_parser.parse(get_attribute(self.__data, 'CityObjects', default=[]))

        return self.__city
