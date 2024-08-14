from src.cityjson import City
from src.cityjson.vertices import VerticesParser
from src.cityjson.geometry import CityGeometryParser
from src.scripts.attribute import get_attribute as get_att
from .templates import GeometryTemplates


class GeometryTemplatesParser:
    def __init__(self, city):
        self.city = city

    # data contains cityjson['geometry-templates']
    def parse(self, data):
        city = City()
        city.scale = [1.0, 1.0, 1.0]

        v_parser = VerticesParser(city)
        city._vertices = v_parser.parse(get_att(data, 'vertices-templates', default=[]))

        gm_parser = CityGeometryParser(city)
        templates_data = get_att(data, 'templates', default=[])
        templates = [gm_parser.parse(template) for template in templates_data]

        return GeometryTemplates(self.city, templates, city._vertices)

