from pathlib import Path

from pycityjson.io import (
    merge_cityjson_directory,
    write_as_cityjson,
)
from pycityjson.model import (
    City,
    CityObject,
    GeometryPrimitive,
    MultiLineString,
    MultiPoint,
    MultiSurface,
    Point,
    Solid,
)

GROUND = Path('tests/test_files/ground')


def _xy_heights(city) -> dict[tuple[float, float], list[float]]:
    """Collect all Z values grouped by X and Y coordinates."""
    heights: dict[tuple[float, float], list[float]] = {}
    for city_object in city.cityobjects:
        for x, y, z in city_object.get_vertices(flatten=True):
            heights.setdefault((x, y), []).append(z)
    return heights


def test_merge_cityjson_directory_keeps_ground_objects_separate():
    city = merge_cityjson_directory(GROUND)

    assert len(city.cityobjects.tolist()) == 2
    assert all(
        city_object.type == 'GroundSurface'
        for city_object in city.cityobjects
    )


def test_merge_cityjson_directory_merges_objects_of_the_same_type():
    city = merge_cityjson_directory(GROUND, merge_objets=True)

    assert len(city.cityobjects.tolist()) == 1
    assert city.cityobjects[0].type == 'GroundSurface'
    assert city.cityobjects[0].geometries[0].primitive.get_type() == 'MultiSurface'
    assert city.cityobjects[0].geometries[0].surface_count() == 450


def test_merge_cityjson_directory_averages_adjacent_ground_vertices():
    city = merge_cityjson_directory(
        GROUND,
        merge_objets=True,
        average_adjacent_vertices=True,
    )
    heights = _xy_heights(city)

    assert heights[(297840.0, 5037000.0)] == [18.280333333333335] * 3


def test_merge_cityjson_directory_returns_a_city_without_writing(tmp_path):
    output_path = tmp_path / 'merged.city.json'

    city = merge_cityjson_directory(GROUND, merge_objets=True)

    assert not output_path.exists()
    write_as_cityjson(city, output_path)
    assert output_path.exists()
    assert len(city.cityobjects.tolist()) == 1


def test_merge_cityjson_promotes_mixed_surface_and_solid_geometries(tmp_path):
    for index, primitive in enumerate([
        MultiSurface([
            MultiLineString([
                MultiPoint([Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0)]),
            ]),
        ]),
        Solid([
            MultiSurface([
                MultiLineString([
                    MultiPoint([Point(0, 0, 1), Point(1, 0, 1), Point(0, 1, 1)]),
                ]),
            ]),
        ]),
    ]):
        source = City()
        city_object = CityObject(source.cityobjects, 'Building', uuid=f'building-{index}')
        city_object.add_geometry(GeometryPrimitive(primitive, '1'))
        source.cityobjects.add_cityobject(city_object)
        write_as_cityjson(source, tmp_path / f'{index}.city.json')

    merged = merge_cityjson_directory(tmp_path, merge_objets=True)

    result = merged.cityobjects[0].geometries[0].primitive
    assert result.get_type() == 'MultiSolid'
    assert len(result.children) == 2
