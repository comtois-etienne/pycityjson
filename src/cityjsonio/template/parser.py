from src.cityjson import City
from src.cityjson.template import GeometryTemplates

from src.cityjsonio.vertices import VerticesParser
from src.cityjsonio.geometry import GeometryParser

from src.scripts.attribute import get_attribute


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

