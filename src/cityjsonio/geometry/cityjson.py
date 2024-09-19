from src.cityjson import City, Vertices
from src.cityjson.geometry import CityGeometry, GeometryPrimitive, GeometryInstance
from src.cityjson.template import GeometryTemplates


class GeometryPrimitiveToCityJsonSerializer:
    def __init__(self, city_vertices: Vertices):
        self.vertices = city_vertices

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


# class GeometryInstanceToCityJsonSerializer:
#     def __init__(self, city_vertices: Vertices):
#         self.city_vertices = city_vertices

#     def serialize(self, geometry_instance: GeometryInstance, template_index: int) -> dict:
#         boundary = self.city_vertices.add(geometry_instance.matrix.get_origin())
#         cityinstance = {
#             'type': 'GeometryInstance',
#             'template': template_index,
#             'boundaries': [boundary],
#             'transformationMatrix': geometry_instance.matrix.recenter().to_cj()
#         }
#         return cityinstance

