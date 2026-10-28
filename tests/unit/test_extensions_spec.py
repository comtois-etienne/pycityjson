import json

from pycityjson import io


def test_extension_declarations_and_custom_root_properties_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'extensions': {
            'noise': {
                'url': 'https://example.org/noise.ext.json',
                'version': '2.0.0',
            },
        },
        '+census': {
            'percent_men': 49.5,
            'percent_women': 50.5,
        },
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'CityObjects': {},
        'vertices': [],
    }
    source_path = tmp_path / 'extensions.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    io.write_as_cityjson(city, saved_path)
    saved = json.loads(saved_path.read_text())

    assert city.extensions == source['extensions']
    assert city.extra_root_properties == {'+census': source['+census']}
    assert saved['extensions'] == source['extensions']
    assert saved['+census'] == source['+census']


def test_extension_custom_city_object_attributes_and_semantics_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'extensions': {
            'thermal': {
                'url': 'https://example.org/thermal.ext.json',
                'version': '1.0.0',
            },
        },
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'vertices': [[0, 0, 0]],
        'CityObjects': {
            'thermal-building': {
                'type': '+ThermalBuilding',
                'attributes': {
                    '+energyClass': {'value': 'A'},
                },
                'geometry': [{
                    'type': 'MultiSurface',
                    'lod': '2',
                    'boundaries': [[[0]]],
                    'semantics': {
                        'surfaces': [{
                            'type': '+ThermalSurface',
                            'azimuth': 180,
                        }],
                        'values': [0],
                    },
                }],
            },
        },
    }
    source_path = tmp_path / 'custom.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    io.write_as_cityjson(city, saved_path)
    saved_object = json.loads(saved_path.read_text())['CityObjects']['thermal-building']

    assert saved_object['type'] == '+ThermalBuilding'
    assert saved_object['attributes']['+energyClass'] == {'value': 'A'}
    assert saved_object['geometry'][0]['semantics']['surfaces'] == [{
        'type': '+ThermalSurface',
        'azimuth': 180,
    }]
