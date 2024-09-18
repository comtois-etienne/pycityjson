from src.cityjson import City

from .cityobjects import CityObjectsParser
from .vertices import VerticesParser
from .template.parser import GeometryTemplateParser

from src.scripts.attribute import (
    get_attribute, 
    get_nested_attribute
)


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

        v_parser = VerticesParser(self.city)
        self.city._vertices = v_parser.parse(get_attribute(self.data, 'vertices', default=[]))

        gt_parser = GeometryTemplateParser(self.city)
        self.city._geometry_template = gt_parser.parse(get_attribute(self.data, 'geometry-templates', default={}))

        co_parser = CityObjectsParser(self.city)
        self.city._cityobjects = co_parser.parse(get_attribute(self.data, 'CityObjects', default=[]))

    def get_city(self) -> City:
        return self.city

