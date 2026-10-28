import json
import zipfile

from pycityjson import io


def test_railway_round_trip_does_not_inject_object_uuids_or_collapse_semantics(tmp_path):
    archive_path = 'tests/test_files/railway.city.json.zip'
    with zipfile.ZipFile(archive_path) as archive:
        source = json.loads(archive.read('railway.city.json'))

    city = io.read_cityjson(archive_path)
    output_path = tmp_path / 'railway.city.json'
    io.write_as_cityjson(city, output_path, purge_vertices=False)
    result = json.loads(output_path.read_text())

    source_object = source['CityObjects']['GMLID_BUI336993_213_9312']
    result_object = result['CityObjects']['GMLID_BUI336993_213_9312']
    assert 'uuid' not in result_object.get('attributes', {})
    assert result_object['geometry'][0]['semantics'] == source_object['geometry'][0]['semantics']


def test_material_value_shorthand_survives_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'appearance': {'materials': [{'name': 'wall'}]},
        'vertices': [[0, 0, 0]],
        'CityObjects': {
            'object': {
                'type': 'GenericCityObject',
                'geometry': [{
                    'type': 'MultiSurface',
                    'lod': '1',
                    'boundaries': [[[0]]],
                    'material': {'visual': {'value': 0}},
                }],
            },
        },
    }
    source_path = tmp_path / 'source.city.json'
    output_path = tmp_path / 'output.city.json'
    source_path.write_text(json.dumps(source))

    io.write_as_cityjson(io.read_cityjson(source_path), output_path)

    result = json.loads(output_path.read_text())
    assert result['CityObjects']['object']['geometry'][0]['material'] == {
        'visual': {'value': 0},
    }


def test_geometry_instance_template_index_survives_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'geometry-templates': {
            'templates': [
                {'type': 'MultiPoint', 'lod': '1', 'boundaries': [0]},
                {'type': 'MultiPoint', 'lod': '1', 'boundaries': [0]},
            ],
            'vertices-templates': [[0, 0, 0]],
        },
        'vertices': [[10, 20, 30]],
        'CityObjects': {
            'object': {
                'type': 'GenericCityObject',
                'geometry': [{
                    'type': 'GeometryInstance',
                    'template': 1,
                    'boundaries': [0],
                    'transformationMatrix': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                }],
            },
        },
    }
    source_path = tmp_path / 'templates.city.json'
    output_path = tmp_path / 'templates-output.city.json'
    source_path.write_text(json.dumps(source))

    io.write_as_cityjson(io.read_cityjson(source_path), output_path)

    result = json.loads(output_path.read_text())
    assert result['CityObjects']['object']['geometry'][0]['template'] == 1
