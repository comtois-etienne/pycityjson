import json

from .city import City
from .cityobjects import CityObjects, CityObjectsParser
from .vertices import Vertices, VerticesParser
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

        city.type = get_attribute(data, 'type', 'CityJSON')
        city.version = get_attribute(data, 'version', '2.0')
        city.metadata = get_attribute(data, 'metadata', {})
        city.scale = get_attribute(data, 'transform', 'scale', [0.001, 0.001, 0.001])
        city.origin = get_attribute(data, 'transform', 'translate', [0, 0, 0])

        v_parser = VerticesParser(city)
        city._vertices = v_parser.parse(get_attribute(data, 'vertices', []))

        co_parser = CityObjectsParser(city)
        city._cityobjects = co_parser.parse(get_attribute(data, 'CityObjects', []))
        
        # city.geometry_template = # todo

        return city

