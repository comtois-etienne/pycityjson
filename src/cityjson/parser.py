import json

from .city import City
from .cityobjects import CityObjects, CityObjectsParser
from .vertices import Vertices, VerticesParser
from .template.parser import GeometryTemplateParser
from src.scripts.attribute import (
    get_attribute, 
    get_nested_attribute
)


class CityParser:
    def __init__(self, json_path):
        self.file_path = json_path
        self.cityjson = None

    def read_json(self):
        with open(self.file_path, 'r') as file:
            self.cityjson = json.load(file)
        return self.cityjson

    def write_json(self, city : City, formatted=False):
        cityjson = city.to_cj()
        pass

    # data contains cityjson
    def parse(self, data) -> City:
        city = City()

        city.type = get_attribute(data, 'type', default='CityJSON')
        city.version = get_attribute(data, 'version', default='2.0')
        city.metadata = get_attribute(data, 'metadata', default={})
        city.scale = get_nested_attribute(data, 'transform', 'scale', default=[0.001, 0.001, 0.001])
        city.origin = get_nested_attribute(data, 'transform', 'translate', default=[0, 0, 0])

        v_parser = VerticesParser(city)
        city._vertices = v_parser.parse(get_attribute(data, 'vertices', default=[]))

        gt_parser = GeometryTemplateParser(city)
        city._geometry_template = gt_parser.parse(get_attribute(data, 'geometry-templates', default={}))

        co_parser = CityObjectsParser(city)
        city._cityobjects = co_parser.parse(get_attribute(data, 'CityObjects', default=[]))

        # city.geometry_template = # todo

        return city

