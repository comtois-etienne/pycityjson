import json
from pycityjson.model import City
from .parser import CityParser
from .cityjson import CitySerializer
from .wavefront import WavefrontSerializer


def read_json(file_path):
    try:
        with open(file_path, 'r') as json_file:
            str_json = json.load(json_file)
    except Exception as e:
        print(f'Error reading JSON file: {e}')
        return None
    return str_json


def write_json(str_json, file_path, indent=0):
    try:
        with open(file_path, 'w') as json_file:
            if indent > 0:
                json.dump(str_json, json_file, indent=indent)
            else:
                json.dump(str_json, json_file)
    except Exception as e:
        print(f'Error writing JSON file: {e}')


def read(file_path) -> City:
    cityjson  = read_json(file_path)
    city_parser = CityParser(cityjson)
    city_parser.parse()
    return city_parser.get_city()


def write_as_cityjson(city: City, file_path, *, purge_vertices=True, pretty=False):
    city_serializer = CitySerializer(city)
    city_dict = city_serializer.serialize(purge_vertices)
    indent = 1 if pretty else 0
    write_json(city_dict, file_path, indent)


def write_as_wavefront(city: City, file_path, as_one_geometry=False):
    wavefront_serializer = WavefrontSerializer(city)
    wavefront_str: list[str] = wavefront_serializer.serialize(as_one_geometry)
    with open(file_path, 'w') as wavefront_file:
        for line in wavefront_str:
            wavefront_file.write(f'{line}\n')


__all__ = [
    'CityParser',
    'CitySerializer',
    'read',
    'write_as_cityjson',
    'write_as_wavefront',
]

