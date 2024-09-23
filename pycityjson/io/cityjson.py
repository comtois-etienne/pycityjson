import numpy as np

from pycityjson.model import (
    City,
    CityGeometry,
    CityGroup,
    CityObject,
    CityObjects,
    GeometryInstance,
    GeometryPrimitive,
    GeometryTemplates,
    TransformationMatrix,
    Vertices,
)


class TransformationMatrixSerializer:
    def serialize(self, matrix: TransformationMatrix) -> dict:
        matrix = matrix.tolist()
        for i in range(16):
            int_val = int(matrix[i])
            flt_val = matrix[i]
            matrix[i] = flt_val if int_val != flt_val else int_val
        return matrix


class CityGeometrySerializer:
    def __init__(self, vertices: Vertices, geometry_templates: GeometryTemplates):
        self.vertices = vertices
        self.geometry_templates = geometry_templates
        self.primitive_serializer = GeometryPrimitiveSerializer(vertices)
        self.instance_serializer = GeometryInstanceSerializer(vertices, geometry_templates)

    def serialize(self, city_geometry: CityGeometry) -> dict:
        if city_geometry.is_geometry_primitive():
            return self.primitive_serializer.serialize(city_geometry)
        else:
            return self.instance_serializer.serialize(city_geometry)


class GeometryPrimitiveSerializer:
    def __init__(self, vertices: Vertices):
        self.vertices = vertices

    def serialize(self, geometry_primitive: GeometryPrimitive) -> dict:
        primitive = geometry_primitive.primitive
        citygeometry = {
            'type': primitive.get_type(),
            'lod': geometry_primitive.lod,
            'boundaries': primitive.index_vertices(self.vertices),
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
        self.vertices = vertices
        self.geometry_templates = geometry_templates
        self.matrix_serializer = TransformationMatrixSerializer()

    def serialize(self, geometry_instance: GeometryInstance) -> dict:
        boundary = self.vertices.add(geometry_instance.matrix.get_origin())
        template_index = self.geometry_templates.add_template(geometry_instance.geometry)
        matrix = self.matrix_serializer.serialize(geometry_instance.matrix.recenter())

        cityinstance = {
            'type': 'GeometryInstance',
            'template': template_index,
            'boundaries': [boundary],
            'transformationMatrix': matrix,
        }
        return cityinstance


class GeometryTemplateSerializer:
    def __init__(self, geometry_template: GeometryTemplates, precision):
        self.geometry_template = geometry_template
        self.serializer = GeometryPrimitiveSerializer(geometry_template.vertices)
        self.precision = precision

    def serialize(self) -> dict:
        templates = [self.serializer.serialize(geometry) for geometry in self.geometry_template.geometries]
        vertices = np.array(self.geometry_template.vertices._vertices)
        vertices = np.round(vertices, self.precision)

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

    def _serialize_cityobject(self, cityobject: CityObject) -> dict:
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

    def _serialize_citygroup(self, citygroup: CityGroup) -> dict:
        cj = self._serialize_cityobject(citygroup)
        if citygroup.children_roles != [] and len(citygroup.children_roles) == len(citygroup.children):
            cj['childrenRoles'] = citygroup.children_roles
        return cj

    def _serialize_one(self, cityobject: CityObject) -> dict:
        if cityobject.type == 'CityObjectGroup':
            return self._serialize_citygroup(cityobject)
        return self._serialize_cityobject(cityobject)

    def serialize(self) -> dict:
        city_objects = {}
        for cityobject in self.cityobjects:
            city_objects[cityobject.uuid()] = self._serialize_one(cityobject)
        return city_objects


class VerticesSerializer:
    def __init__(self, vertices: Vertices, origin=None, scale=None):
        self.vertices = vertices
        self.origin = [0, 0, 0] if origin is None else origin
        self.scale = [0.001, 0.001, 0.001] if scale is None else scale

    def serialize(self) -> list:
        vertices = np.array(self.vertices._vertices)
        vertices = (vertices - np.array(self.origin)) / np.array(self.scale)
        vertices = np.round(vertices).astype(int)
        return vertices.tolist()


class CitySerializer:
    def __init__(self, city: City):
        self.city = city

    def serialize(self, purge_vertices=True) -> dict:
        if purge_vertices:
            self.city.vertices = Vertices()
            self.city.geometry_templates.vertices = Vertices()

        cityobjects_serializer = CityObjectsSerializer(self.city.cityobjects, self.city.vertices, self.city.geometry_templates)

        vertices_serializer = VerticesSerializer(self.city.vertices, self.city.origin, self.city.scale)

        geometry_template_serializer = GeometryTemplateSerializer(self.city.geometry_templates, self.city.precision())

        city_dict = {
            'type': self.city.type,
            'version': self.city.version,
            'CityObjects': cityobjects_serializer.serialize(),
            'transform': {'scale': self.city.scale, 'translate': self.city.origin},
            'vertices': vertices_serializer.serialize(),
        }
        if not self.city.geometry_templates.is_empty():
            city_dict['geometry-templates'] = geometry_template_serializer.serialize()
        city_dict['metadata'] = self.city.metadata

        return city_dict
