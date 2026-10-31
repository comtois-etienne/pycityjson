from pathlib import Path

from pycityjson.io import read_geojson, reproject_coordinates

GEOJSON = Path('tests/test_files/quartierreferencehabitation.geojson')


def test_read_geojson_loads_features_and_properties():
    city = read_geojson(GEOJSON, epsg=4326)

    assert len(city.cityobjects) == 91
    city_object = city.cityobjects[0]
    assert city_object.attributes['nom_mun'] == 'Montréal'
    assert city_object.geometries[0].primitive.get_type() == 'MultiSurface'
    assert city.metadata['geojson']['properties'][city_object.uuid()] == city_object.attributes
    assert city.epsg() == 4326


def test_read_geojson_reprojects_feature_coordinates():
    city = read_geojson(GEOJSON, epsg=4326, convert_to_epsg=2950)
    point = city.cityobjects[0].get_vertices(flatten=True)[0]

    assert 250000 < point[0] < 350000
    assert 5000000 < point[1] < 5100000
    assert city.epsg() == 2950


def test_reproject_coordinates_preserves_nested_shape_and_dimensions():
    coordinates = [[[-73.5, 45.5, 12.0]]]

    result = reproject_coordinates(coordinates, 4326, 2950)

    assert len(result) == 1
    assert len(result[0]) == 1
    assert result[0][0][2] == 12.0
