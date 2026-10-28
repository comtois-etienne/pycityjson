import json
import os
import tarfile
import zipfile
from collections.abc import Iterator

from pycityjson.model import City

from .cityjson_input import CityParser
from .cityjson_output import CitySerializer
from .wavefront_output import WavefrontSerializer


def _read_json(file_path: str | os.PathLike[str]) -> dict | None:
    """
    Reads a JSON file and returns it as a dictionary
    :param file_path: path to the JSON file
    """
    try:
        path = os.fspath(file_path)
        if path.endswith('.zip'):
            with zipfile.ZipFile(path) as archive:
                members = [member for member in archive.namelist() if member.endswith('.city.json')]
                if not members:
                    raise ValueError(f'No .city.json file found in archive: {path}')
                str_json = json.loads(archive.read(members[0]))
        elif path.endswith('.tar'):
            with tarfile.open(path, 'r') as archive:
                members = [member for member in archive.getmembers() if member.isfile() and member.name.endswith('.city.json')]
                if not members:
                    raise ValueError(f'No .city.json file found in archive: {path}')
                file = archive.extractfile(members[0])
                if file is None:
                    raise ValueError(f'Unable to read .city.json file in archive: {path}')
                str_json = json.load(file)
        else:
            with open(path, 'r') as json_file:
                str_json = json.load(json_file)
    except Exception as e:
        print(f'Error reading JSON file: {e}')
        return None
    return str_json


def _write_json(str_json: dict, file_path: str, indent=0):
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
                json.dump(str_json, json_file, separators=(',', ':'))
    except Exception as e:
        print(f'Error writing JSON file: {e}')


def read_cityjson(file_path: str | os.PathLike[str], add_uuid: bool = False) -> City:
    """
    Reads a CityJSON and parses it into a City object
    :param file_path: path to a CityJSON, `.city.json`, `.city.json.zip`, or `.city.json.tar` file
    :param add_uuid: add UUIDs to semantic objects that do not have one
    """
    cityjson = _read_json(file_path)
    city_parser = CityParser(cityjson)
    return city_parser.parse(add_uuid=add_uuid)


def read_cityjson_features(file_path: str | os.PathLike[str]) -> Iterator[dict]:
    """
    Lazily reads a CityJSON JSON Lines stream.

    The first non-empty line must be a CityJSON object containing the required
    header members. Subsequent lines must be CityJSONFeature objects.
    """
    path = os.fspath(file_path)

    def objects() -> Iterator[dict]:
        with open(path, 'r') as json_file:
            for line_number, line in enumerate(json_file, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f'Invalid JSON on line {line_number}') from error
                if not isinstance(value, dict):
                    raise ValueError(f'JSON Lines entry on line {line_number} must be an object')
                yield value

    stream = objects()
    try:
        header = next(stream)
    except StopIteration as error:
        raise ValueError('CityJSONFeature stream is empty') from error

    if header.get('type') != 'CityJSON':
        raise ValueError('The first JSON Lines entry must be a CityJSON object')
    required = {'version', 'transform', 'CityObjects', 'vertices'}
    missing = required.difference(header)
    if missing:
        raise ValueError(f'CityJSON header is missing required members: {sorted(missing)}')
    yield header

    for feature in stream:
        if feature.get('type') != 'CityJSONFeature':
            raise ValueError('Subsequent JSON Lines entries must be CityJSONFeature objects')
        required = {'id', 'CityObjects', 'vertices'}
        missing = required.difference(feature)
        if missing:
            raise ValueError(f'CityJSONFeature is missing required members: {sorted(missing)}')
        forbidden = {'transform', 'version', 'metadata', 'geometry-templates', 'extensions'}
        present_forbidden = forbidden.intersection(feature)
        if present_forbidden:
            raise ValueError(
                f'CityJSONFeature contains forbidden members: {sorted(present_forbidden)}',
            )
        yield feature


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
    _write_json(city_dict, file_path, indent)


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
    'read_cityjson_features',
    'write_as_cityjson',
    'write_as_wavefront',
]
