from pathlib import Path

from pycityjson.io import read_cityjson, reproject_coordinates

CITYJSON = Path('tests/test_files/quartierreferencehabitation.city.json')
OBJECT_UUID = '0YCVPaFLTFNuyHhJM0rLEq'


def _coordinate(longitude: float, latitude: float) -> list[float]:
    """Convert a WGS84 coordinate to the reference city's EPSG."""
    return reproject_coordinates([longitude, latitude], 4326, 2950)


def test_city_and_object_containment_use_polygon_boundaries():
    city = read_cityjson(CITYJSON)
    city_object = city.cityobjects[OBJECT_UUID]
    inside = _coordinate(-73.754469, 45.515978)
    outside = _coordinate(-73.751922, 45.516256)
    distant = _coordinate(-73.993480, 45.430651)

    assert city.is_coordinate_inside(inside)
    assert city_object.is_coordinate_inside(inside)
    assert city_object.geometries[0].is_coordinate_inside(inside)
    assert not city.is_coordinate_inside(outside)
    assert not city_object.is_coordinate_inside(outside)
    assert not city.is_coordinate_inside(distant)
    assert not city_object.is_coordinate_inside(distant)


def test_bounding_box_containment_uses_all_vertices_without_recursion():
    city = read_cityjson(CITYJSON)
    city_object = city.cityobjects[OBJECT_UUID]
    inside = _coordinate(-73.754469, 45.515978)
    outside_polygon_inside_box = _coordinate(-73.751922, 45.516256)
    distant = _coordinate(-73.993480, 45.430651)

    assert city.is_coordinate_inside(inside, bounding_box=True)
    assert city_object.is_coordinate_inside(inside, bounding_box=True)
    assert city_object.geometries[0].is_coordinate_inside(inside, bounding_box=True)
    assert city.is_coordinate_inside(outside_polygon_inside_box, bounding_box=True)
    assert city_object.is_coordinate_inside(outside_polygon_inside_box, bounding_box=True)
    assert not city.is_coordinate_inside(distant, bounding_box=True)
