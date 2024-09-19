from src.cityjson import City, Vertices
from src.cityjson.geometry import CityGeometry, GeometryPrimitive, GeometryInstance, TransformationMatrix
from src.cityjson.template import GeometryTemplates


class MatrixToCityJsonSerializer:
    def serialize(self, matrix: TransformationMatrix) -> dict:
        matrix = matrix.tolist()
        for i in range(16):
            int_val = int(matrix[i])
            flt_val = matrix[i]
            matrix[i] = flt_val if int_val != flt_val else int_val
        return matrix


class CityGeometryToCityJsonSerializer:
    def __init__(self, vertices: Vertices, geometry_templates: GeometryTemplates):
        self.vertices = vertices
        self.geometry_templates = geometry_templates
        self.primitive_serializer = GeometryPrimitiveToCityJsonSerializer(vertices)
        self.instance_serializer = GeometryInstanceToCityJsonSerializer(vertices, geometry_templates)

    def serialize(self, city_geometry: CityGeometry) -> dict:
        if city_geometry.is_geometry_primitive():
            return self.primitive_serializer.serialize(city_geometry)
        else:
            return self.instance_serializer.serialize(city_geometry)


class GeometryPrimitiveToCityJsonSerializer:
    def __init__(self, vertices: Vertices):
        self.vertices = vertices

    def serialize(self, geometry_primitive: GeometryPrimitive) -> dict:
        primitive = geometry_primitive.primitive
        citygeometry = {
            'type': primitive.get_type(),
            'lod': geometry_primitive.lod,
            'boundaries': primitive.index_vertices(self.vertices)
        }
        semantics = primitive.get_semantic_surfaces()
        if semantics is not None:
            citygeometry['semantics'] = {
                'surfaces': semantics,
                'values': primitive.get_semantic_values(semantics)
            }
        return citygeometry


class GeometryInstanceToCityJsonSerializer:
    def __init__(self, vertices: Vertices, geometry_templates: GeometryTemplates):
        self.vertices = vertices
        self.geometry_templates = geometry_templates
        self.matrix_serializer = MatrixToCityJsonSerializer()

    def serialize(self, geometry_instance: GeometryInstance) -> dict:
        boundary = self.vertices.add(geometry_instance.matrix.get_origin())
        template_index = self.geometry_templates.add_template(geometry_instance.geometry)
        matrix = self.matrix_serializer.serialize(geometry_instance.matrix.recenter())

        cityinstance = {
            'type': 'GeometryInstance',
            'template': template_index,
            'boundaries': [boundary],
            'transformationMatrix': matrix
        }
        return cityinstance

