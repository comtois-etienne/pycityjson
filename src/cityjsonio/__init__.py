from src.cityjson import City
from src.scripts.jsonio import read_json
from .parser import CityParser


def read(file_path) -> City:
    cityjson  = read_json(file_path)
    city_parser = CityParser(cityjson)
    city_parser.parse()
    return city_parser.get_city()


__all__ = [
    'CityParser',
    'read'
]

