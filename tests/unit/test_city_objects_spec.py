import json

from pycityjson import io


def test_city_object_relationships_and_attributes_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'CityObjects': {
            'building': {
                'type': 'Building',
                'attributes': {'custom': {'value': 3}, 'tags': ['a', 'b']},
                'geographicalExtent': [0, 0, 0, 2, 3, 4],
                'children': ['part'],
                'address': [{'city': 'Montreal', 'location': {'type': 'MultiPoint'}}],
            },
            'part': {
                'type': 'BuildingPart',
                'parents': ['building'],
            },
        },
        'vertices': [],
    }
    source_path = tmp_path / 'objects.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    building = city.cityobjects['building']
    part = city.cityobjects['part']

    assert building.children == [part]
    assert part.parents == [building]
    assert {key: value for key, value in building.attributes.items() if key != 'uuid'} == (
        source['CityObjects']['building']['attributes']
    )
    assert building.geo_extent == source['CityObjects']['building']['geographicalExtent']
    assert building.address == source['CityObjects']['building']['address']

    io.write_as_cityjson(city, saved_path)
    saved = json.loads(saved_path.read_text())
    assert saved['CityObjects']['part']['parents'] == ['building']
    assert 'parent' not in saved['CityObjects']['part']
    assert saved['CityObjects']['building']['address'] == source['CityObjects']['building']['address']


def test_city_object_group_roles_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'CityObjects': {
            'group': {
                'type': 'CityObjectGroup',
                'children': ['one', 'two'],
                'children_roles': ['residential', 'commercial'],
            },
            'one': {'type': 'Building', 'parents': ['group']},
            'two': {'type': 'LandUse', 'parents': ['group']},
        },
        'vertices': [],
    }
    source_path = tmp_path / 'group.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    group = city.cityobjects['group']
    assert group.children_roles == source['CityObjects']['group']['children_roles']

    io.write_as_cityjson(city, saved_path)
    saved = json.loads(saved_path.read_text())
    assert saved['CityObjects']['group']['children_roles'] == source['CityObjects']['group']['children_roles']
    assert 'childrenRoles' not in saved['CityObjects']['group']
