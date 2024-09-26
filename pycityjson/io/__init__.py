import json

from pycityjson.model import City

from .cityjson_input import CityParser
from .cityjson_output import CitySerializer
from .wavefront_output import WavefrontSerializer


def read_json(file_path: str) -> dict:
    """
    Reads a JSON file and returns it as a dictionary
    :param file_path: path to the JSON file
    """
    try:
        with open(file_path, 'r') as json_file:
            str_json = json.load(json_file)
    except Exception as e:
        print(f'Error reading JSON file: {e}')
        return None
    return str_json


def write_json(str_json: dict, file_path: str, indent=0):
    """
    Writes a dictionary as a JSON file
    :param str_json: dictionary to be written
    :param file_path: path to the JSON file
    :param indent: indentation level. If 0, no indentation is used
    """
    try:
        with open(file_path, 'w') as json_file:
            if indent > 0:
                json.dump(str_json, json_file, indent=indent)
            else:
                json.dump(str_json, json_file)
    except Exception as e:
        print(f'Error writing JSON file: {e}')


def read_cityjson(file_path: str) -> City:
    """
    Reads a CityJSON and parses it into a City object
    :param file_path: path to the CityJSON file
    """
    cityjson = read_json(file_path)
    city_parser = CityParser(cityjson)
    return city_parser.parse()


def write_as_cityjson(city: City, file_path, *, purge_vertices=True, pretty=False):
    """
    Writes a City object as a CityJSON file
    :param city: City object to be written
    :param file_path: path to the CityJSON file
    :param purge_vertices: if True, the un-used vertices are removed from the CityJSON. They may be used by unsupported extensions.
    :param pretty: if True, the JSON is written with one space indentation
    """
    city_serializer = CitySerializer(city)
    city_dict = city_serializer.serialize(purge_vertices)
    indent = 1 if pretty else 0
    write_json(city_dict, file_path, indent)


def write_as_wavefront(city: City, file_path, *, as_one_geometry=False, swap_yz=False):
    """
    Writes a City object as a Wavefront OBJ file. Some CityJSON features are not supported in Wavefront OBJ.
    :param city: City object to be written
    :param file_path: path to the Wavefront OBJ file
    :param as_one_geometry: if True, all geometries are written as a single geometry. Otherwise, each object has its own 'o' line with a 'g' line for each geometry
    :param swap_yz: if True, the Y and Z coordinates are swapped for wavefront visualization
    """
    wavefront_serializer = WavefrontSerializer(city)
    wavefront_str: list[str] = wavefront_serializer.serialize(as_one_geometry=as_one_geometry, swap_yz=swap_yz)
    with open(file_path, 'w') as wavefront_file:
        for line in wavefront_str:
            wavefront_file.write(f'{line}\n')


__all__ = [
    'CityParser',
    'CitySerializer',
    'read_cityjson',
    'write_as_cityjson',
    'write_as_wavefront',
]
