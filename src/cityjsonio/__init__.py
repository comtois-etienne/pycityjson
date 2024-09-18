from src.cityjson import City
from src.scripts.jsonio import read_json, write_json
from .parser import CityParser
from .cityjson import CityToCityJsonSerializer


def read(file_path) -> City:
    cityjson  = read_json(file_path)
    city_parser = CityParser(cityjson)
    city_parser.parse()
    return city_parser.get_city()


def write_as_cityjson(city: City, file_path, *, purge_vertices=True, pretty=False):
    city_serializer = CityToCityJsonSerializer(city)
    city_dict = city_serializer.serialize(purge_vertices)
    indent = 1 if pretty else 0
    write_json(city_dict, file_path, indent)


def write_as_wavefront(city: City, file_path):
    pass


__all__ = [
    'CityParser',
    'CityToCityJsonSerializer',
    'read',
]

