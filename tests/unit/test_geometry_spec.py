import json

from pycityjson import io
from pycityjson.model import (
    City,
    CityObject,
    GeometryPrimitive,
    MultiLineString,
    MultiPoint,
    MultiSolid,
    MultiSurface,
    Point,
    Semantic,
    Solid,
)


def _line(semantic=None):
    return MultiLineString(
        [MultiPoint([Point(0, 0, 0), Point(1, 0, 0)])],
        semantic=semantic,
    )


def test_geometry_semantics_preserve_null_values_for_unassigned_surfaces():
    first = _line(Semantic('WallSurface', add_uuid=False))
    second = _line()
    geometry = GeometryPrimitive(MultiSurface([first, second]))

    semantics = geometry.primitive.get_semantic_surfaces()

    assert semantics == [{'type': 'WallSurface'}]
    assert geometry.primitive.get_semantic_values(semantics) == [0, None]


def test_multilinestring_supports_geometry_semantics():
    semantic = Semantic('TrafficArea', add_uuid=False)
    geometry = GeometryPrimitive(MultiLineString([MultiPoint([Point(0, 0, 0)])], semantic=semantic))

    assert geometry.primitive.get_semantic_surfaces() == [{'type': 'TrafficArea'}]
    assert geometry.primitive.get_semantic_values([{'type': 'TrafficArea'}]) == 0


def test_multipoint_semantics_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'vertices': [[0, 0, 0], [1, 0, 0]],
        'CityObjects': {
            'points': {
                'type': 'GenericCityObject',
                'geometry': [{
                    'type': 'MultiPoint',
                    'lod': '1',
                    'boundaries': [0, 1],
                    'semantics': {
                        'surfaces': [{'type': '+Tree'}, {'type': '+Lamp'}],
                        'values': [0, 1],
                    },
                }],
            },
        },
    }
    source_path = tmp_path / 'multipoint.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    geometry = city.cityobjects['points'].geometries[0]
    assert geometry.primitive.get_semantic_surfaces() == source['CityObjects']['points']['geometry'][0]['semantics']['surfaces']
    assert geometry.primitive.get_semantic_values(geometry.primitive.get_semantic_surfaces()) == [0, 1]

    io.write_as_cityjson(city, saved_path)
    saved = json.loads(saved_path.read_text())
    assert saved['CityObjects']['points']['geometry'][0]['semantics'] == source['CityObjects']['points']['geometry'][0]['semantics']


def test_multilinestring_semantics_apply_to_each_line(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'vertices': [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        'CityObjects': {
            'lines': {
                'type': 'GenericCityObject',
                'geometry': [{
                    'type': 'MultiLineString',
                    'lod': '1',
                    'boundaries': [[0, 1], [1, 2]],
                    'semantics': {
                        'surfaces': [{'type': '+RoadEdge'}, {'type': '+RailEdge'}],
                        'values': [0, 1],
                    },
                }],
            },
        },
    }
    source_path = tmp_path / 'lines.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    geometry = city.cityobjects['lines'].geometries[0]
    semantics = geometry.primitive.get_semantic_surfaces()
    assert semantics == source['CityObjects']['lines']['geometry'][0]['semantics']['surfaces']
    assert geometry.primitive.get_semantic_values(semantics) == [0, 1]

    io.write_as_cityjson(city, saved_path)
    saved = json.loads(saved_path.read_text())
    assert saved['CityObjects']['lines']['geometry'][0]['semantics'] == source['CityObjects']['lines']['geometry'][0]['semantics']


def test_all_solid_geometry_types_have_specification_types():
    surface = MultiSurface([_line()])
    solid = Solid([surface])
    multi_solid = MultiSolid([solid])

    assert surface.get_type() == 'MultiSurface'
    assert solid.get_type() == 'Solid'
    multi_solid.type = 'CompositeSolid'
    assert multi_solid.get_type() == 'CompositeSolid'


def test_semantics_round_trip_without_inventing_uuid(tmp_path):
    city = City()
    city.vertices.add([0, 0, 0])
    city.vertices.add([1, 0, 0])
    city.cityobjects.add_cityobject(
        CityObject(
            city.cityobjects,
            'GenericCityObject',
            {'uuid': 'object-1'},
            [
                GeometryPrimitive(
                    MultiLineString(
                        [MultiPoint([Point(0, 0, 0), Point(1, 0, 0)])],
                        semantic=Semantic('WallSurface', add_uuid=False),
                    ),
                ),
            ],
        ),
    )
    path = tmp_path / 'semantic.city.json'

    io.write_as_cityjson(city, path)
    saved = json.load(open(path))

    assert saved['CityObjects']['object-1']['geometry'][0]['semantics']['surfaces'] == [{'type': 'WallSurface'}]


def test_read_cityjson_add_uuid_is_opt_in(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'vertices': [[0, 0, 0]],
        'CityObjects': {
            'object-1': {
                'type': 'GenericCityObject',
                'geometry': [
                    {
                        'type': 'MultiSurface',
                        'lod': '1',
                        'boundaries': [[[0]]],
                        'semantics': {
                            'surfaces': [{'type': 'WallSurface'}],
                            'values': [0],
                        },
                    },
                ],
            },
        },
    }
    path = tmp_path / 'semantic.city.json'
    path.write_text(json.dumps(source))

    without_uuid = io.read_cityjson(path)
    with_uuid = io.read_cityjson(path, add_uuid=True)
    default_semantic = without_uuid.cityobjects['object-1'].geometries[0].get_surfaces()[0].semantic
    generated_semantic = with_uuid.cityobjects['object-1'].geometries[0].get_surfaces()[0].semantic

    assert 'uuid' not in default_semantic.to_dict()
    assert 'uuid' in generated_semantic.to_dict()


def test_read_write_without_add_uuid_does_not_add_semantic_uuid(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'vertices': [[0, 0, 0]],
        'CityObjects': {
            'object-1': {
                'type': 'GenericCityObject',
                'geometry': [
                    {
                        'type': 'MultiSurface',
                        'lod': '1',
                        'boundaries': [[[0]]],
                        'semantics': {
                            'surfaces': [{'type': 'WallSurface'}],
                            'values': [0],
                        },
                    },
                ],
            },
        },
    }
    source_path = tmp_path / 'source.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    io.write_as_cityjson(city, saved_path)
    saved = json.load(open(saved_path))

    assert saved['CityObjects']['object-1']['geometry'][0]['semantics']['surfaces'] == [{'type': 'WallSurface'}]


def test_read_write_with_add_uuid_persists_generated_semantic_uuid(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'vertices': [[0, 0, 0]],
        'CityObjects': {
            'object-1': {
                'type': 'GenericCityObject',
                'geometry': [
                    {
                        'type': 'MultiSurface',
                        'lod': '1',
                        'boundaries': [[[0]]],
                        'semantics': {
                            'surfaces': [{'type': 'WallSurface'}],
                            'values': [0],
                        },
                    },
                ],
            },
        },
    }
    source_path = tmp_path / 'source.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path, add_uuid=True)
    generated_uuid = city.cityobjects['object-1'].geometries[0].get_surfaces()[0].semantic['uuid']
    io.write_as_cityjson(city, saved_path)

    saved = json.load(open(saved_path))
    reread = io.read_cityjson(saved_path)
    reread_uuid = reread.cityobjects['object-1'].geometries[0].get_surfaces()[0].semantic['uuid']

    assert saved['CityObjects']['object-1']['geometry'][0]['semantics']['surfaces'][0]['uuid'] == generated_uuid
    assert reread_uuid == generated_uuid
