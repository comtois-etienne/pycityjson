import json

import pytest

from pycityjson import io


def test_minimal_cityjson_object_can_be_read_and_written(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {
            'scale': [1.0, 1.0, 1.0],
            'translate': [0.0, 0.0, 0.0],
        },
        'CityObjects': {},
        'vertices': [],
    }
    source_path = tmp_path / 'minimal.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    io.write_as_cityjson(city, saved_path, purge_vertices=False)
    saved = json.loads(saved_path.read_text())

    assert saved['type'] == 'CityJSON'
    assert saved['version'] == '2.0'
    assert saved['transform'] == source['transform']
    assert saved['CityObjects'] == {}
    assert saved['vertices'] == []


def test_optional_cityjson_members_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'extensions': {
            'https://www.cityjson.org/extension/Example.json': '1.0',
        },
        'transform': {
            'scale': [0.1, 0.1, 0.1],
            'translate': [100.0, 200.0, 300.0],
        },
        'metadata': {
            'identifier': 'example',
            'referenceSystem': 'https://www.opengis.net/def/crs/EPSG/0/4326',
        },
        'CityObjects': {},
        'vertices': [],
        'appearance': {},
        'geometry-templates': {},
    }
    source_path = tmp_path / 'complete.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    io.write_as_cityjson(city, saved_path, purge_vertices=False)
    saved = json.loads(saved_path.read_text())

    assert city.extensions == source['extensions']
    assert city.metadata == source['metadata']
    assert saved['extensions'] == source['extensions']
    assert saved['metadata'] == source['metadata']


def test_transform_decodes_each_axis_without_rounding_coordinates(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {
            'scale': [0.1, 0.01, 0.001],
            'translate': [100.1234, 200.56789, 300.123456],
        },
        'CityObjects': {},
        'vertices': [[1, 2, 3]],
    }
    source_path = tmp_path / 'transformed.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)

    assert city.vertices[0] == pytest.approx([100.2234, 200.58789, 300.126456])

    io.write_as_cityjson(city, saved_path, purge_vertices=False)
    saved = json.loads(saved_path.read_text())
    assert saved['transform'] == source['transform']
    assert saved['vertices'] == source['vertices']
