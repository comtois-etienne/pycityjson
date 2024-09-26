import numpy as np

from pycityjson.model import (
    City,
    CityGeometry,
    CityObject,
    CityObjectGroup,
    CityObjects,
    GeometryInstance,
    GeometryPrimitive,
    GeometryTemplates,
    Primitive,
    TransformationMatrix,
    Vertex,
    Vertices,
)


class TransformationMatrixSerializer:
    def serialize(self, matrix: TransformationMatrix) -> list[float | int]:
        matrix = matrix.tolist()
        for i in range(16):
            int_val = int(matrix[i])
            flt_val = matrix[i]
            matrix[i] = flt_val if int_val != flt_val else int_val
        return matrix


class CityGeometrySerializer:
    def __init__(self, vertices: Vertices, geometry_templates: GeometryTemplates):
        self.__primitive_serializer = GeometryPrimitiveSerializer(vertices)
        self.__instance_serializer = GeometryInstanceSerializer(vertices, geometry_templates)

    def serialize(self, city_geometry: CityGeometry) -> dict:
        """
        :param city_geometry: CityGeometry to be serialized
        """
        if city_geometry.is_geometry_primitive():
            return self.__primitive_serializer.serialize(city_geometry)
        else:
            return self.__instance_serializer.serialize(city_geometry)


class GeometryPrimitiveSerializer:
    def __init__(self, vertices: Vertices):
        self.__vertices = vertices

    def serialize(self, geometry_primitive: GeometryPrimitive) -> dict:
        """
        :param geometry_primitive: GeometryPrimitive to be serialized
        """
        primitive: Primitive = geometry_primitive.primitive
        citygeometry = {
            'type': primitive.get_type(),
            'lod': geometry_primitive.lod,
            'boundaries': primitive.index_vertices(self.__vertices),
        }
        semantics = primitive.get_semantic_surfaces()
        if semantics is not None:
            citygeometry['semantics'] = {
                'surfaces': semantics,
                'values': primitive.get_semantic_values(semantics),
            }
        return citygeometry


class GeometryInstanceSerializer:
    def __init__(self, vertices: Vertices, geometry_templates: GeometryTemplates):
        self.__vertices = vertices
        self.__geometry_templates = geometry_templates
        self.__matrix_serializer = TransformationMatrixSerializer()

    def serialize(self, geometry_instance: GeometryInstance) -> dict:
        """
        :param geometry_instance: GeometryInstance to be serialized
        """
        boundary = self.__vertices.add(geometry_instance.matrix.get_origin())
        template_index = self.__geometry_templates.add_template(geometry_instance.geometry)
        matrix = self.__matrix_serializer.serialize(geometry_instance.matrix.recenter())

        cityinstance = {
            'type': 'GeometryInstance',
            'template': template_index,
            'boundaries': [boundary],
            'transformationMatrix': matrix,
        }
        return cityinstance


class GeometryTemplateSerializer:
    def __init__(self, geometry_template: GeometryTemplates, precision: int):
        """
        :param geometry_template: GeometryTemplates to be serialized
        :param precision: the number of decimal places to round the vertices. Must be a positive integer [0, infinity]
        """
        self.__geometry_template = geometry_template
        self.__serializer = GeometryPrimitiveSerializer(geometry_template.vertices)
        self.__precision = precision

    def serialize(self) -> dict:
        templates = [self.__serializer.serialize(geometry) for geometry in self.__geometry_template.geometries]
        vertices = np.array(self.__geometry_template.vertices.tolist())
        vertices = np.round(vertices, self.__precision)

        return {'templates': templates, 'vertices-templates': vertices.tolist()}


class CityObjectsSerializer:
    def __init__(
        self,
        cityobjects: CityObjects,
        vertices: Vertices,
        geometry_templates: GeometryTemplates,
    ):
        self.cityobjects = cityobjects
        self.serializer = CityGeometrySerializer(vertices, geometry_templates)

    def __serialize_cityobject(self, cityobject: CityObject) -> dict:
        """
        :param cityobject: CityObject to be serialized
        """
        cj = {'type': cityobject.type}
        if cityobject.geo_extent is not None:
            cj['geographicalExtent'] = cityobject.geo_extent
        if cityobject.attributes != {}:
            cj['attributes'] = cityobject.attributes
        if len(cityobject.geometries) > 0:
            cj['geometry'] = [self.serializer.serialize(g) for g in cityobject.geometries]
        if cityobject.children != []:
            cj['children'] = [child.uuid() for child in cityobject.children]
        if cityobject.parents != []:
            cj['parent'] = [parent.uuid() for parent in cityobject.parents]
        return cj

    def __serialize_cityobjectgroup(self, cityobjectgroup: CityObjectGroup) -> dict:
        """
        :param cityobjectgroup: CityObjectGroup to be serialized
        """
        cj = self.__serialize_cityobject(cityobjectgroup)
        if cityobjectgroup.children_roles != [] and len(cityobjectgroup.children_roles) == len(cityobjectgroup.children):
            cj['childrenRoles'] = cityobjectgroup.children_roles
        return cj

    def __serialize_one(self, cityobject: CityObject) -> dict:
        """
        :param cityobject: CityObject or CityObjectGroup to be serialized
        """
        if cityobject.type == 'CityObjectGroup':
            return self.__serialize_cityobjectgroup(cityobject)
        return self.__serialize_cityobject(cityobject)

    def serialize(self) -> dict:
        city_objects = {}
        for cityobject in self.cityobjects:
            city_objects[cityobject.uuid()] = self.__serialize_one(cityobject)
        return city_objects


class VerticesSerializer:
    def __init__(self, vertices: Vertices, origin: Vertex = None, scale: Vertex = None):
        self.vertices = vertices
        self.origin = [0, 0, 0] if origin is None else origin
        self.scale = [0.001, 0.001, 0.001] if scale is None else scale

    def serialize(self) -> list[list[int]]:
        """
        Returns the vertices as a list of lists of integers.
        The vertices are scaled and translated according to the origin and scale.
        """
        vertices = np.array(self.vertices.tolist())
        vertices = (vertices - np.array(self.origin)) / np.array(self.scale)
        vertices = np.round(vertices).astype(int)
        return vertices.tolist()


class CitySerializer:
    def __init__(self, city: City):
        self.__city: City = city

    def serialize(self, purge_vertices=True) -> dict:
        """
        Converts the City into a CityJSON dictionary.
        :param purge_vertices: if True, the un-used vertices are removed from the CityJSON. They may be used by unsupported extensions.
        """
        if purge_vertices:
            self.__city.vertices = Vertices(precision=self.__city.precision())
            self.__city.geometry_templates.vertices = Vertices(precision=self.__city.precision())

        cityobjects_serializer = CityObjectsSerializer(self.__city.cityobjects, self.__city.vertices, self.__city.geometry_templates)
        vertices_serializer = VerticesSerializer(self.__city.vertices, self.__city.origin, self.__city.scale)
        geometry_template_serializer = GeometryTemplateSerializer(self.__city.geometry_templates, self.__city.precision())

        city_dict = {
            'type': self.__city.type,
            'version': self.__city.version,
            'transform': {'scale': self.__city.scale, 'translate': self.__city.origin},
        }

        # WARNING: Serialization order matters
        city_dict['CityObjects'] = cityobjects_serializer.serialize()
        city_dict['vertices'] = vertices_serializer.serialize()

        if not self.__city.geometry_templates.is_empty():
            city_dict['geometry-templates'] = geometry_template_serializer.serialize()

        city_dict['metadata'] = self.__city.metadata

        return city_dict
