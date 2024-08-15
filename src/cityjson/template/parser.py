from src.cityjson import City
from src.cityjson.vertices import VerticesParser
from src.cityjson.geometry import GeometryParser
from src.scripts.attribute import get_attribute
from .template import GeometryTemplate


class GeometryTemplateParser:
    def __init__(self, city):
        self.city = city

    # data contains cityjson['geometry-templates']
    def parse(self, data) -> GeometryTemplate:
        city = City()
        city.scale = [1.0, 1.0, 1.0]

        v_parser = VerticesParser(city)
        city._vertices = v_parser.parse(get_attribute(data, 'vertices-templates', default=[]))

        gm_parser = GeometryParser(city)
        templates_data = get_attribute(data, 'templates', default=[])
        templates = [gm_parser.parse(template) for template in templates_data]

        return GeometryTemplate(self.city, templates, city._vertices)

