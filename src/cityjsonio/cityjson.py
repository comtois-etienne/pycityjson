from src.cityjson import City, Vertices

from src.cityjsonio.cityobjects import CityObjectsToCityJsonSerializer as CityObjectsSerializer
from src.cityjsonio.vertices import VerticesToCityJsonSerializer as VerticesSerializer
from src.cityjsonio.template import GeometryTemplateToCityJsonSerializer as GeometryTemplateSerializer


class CityToCityJsonSerializer:
    def __init__(self, city: City):
        self.city = city

    def serialize(self, purge_vertices=True) -> dict:
        if purge_vertices:
            self.city.vertices = Vertices()
            self.city.geometry_templates.vertices = Vertices()

        cityobjects_serializer = CityObjectsSerializer(self.city.cityobjects, self.city)
        vertices_serializer = VerticesSerializer(self.city.vertices, self.city.origin, self.city.scale)
        geometry_template_serializer = GeometryTemplateSerializer(self.city.geometry_templates, self.city.precision())

        city_dict = {
            'type': self.city.type,
            'version': self.city.version,
            'CityObjects': cityobjects_serializer.serialize(),
            'transform': {
                'scale': self.city.scale,
                'translate': self.city.origin
            },
            'vertices': vertices_serializer.serialize()
        }
        if not self.city.geometry_templates.is_empty():
            city_dict['geometry-templates'] = geometry_template_serializer.serialize()
        city_dict['metadata'] = self.city.metadata

        return city_dict

