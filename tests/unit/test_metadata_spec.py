import json

from pycityjson import io
from pycityjson.model import City


def test_all_core_metadata_properties_round_trip(tmp_path):
    metadata = {
        'geographicalExtent': [10.1, 20.2, -3.0, 40.4, 50.5, 6.0],
        'identifier': 'dataset-123',
        'pointOfContact': {
            'contactName': 'Example Organization',
            'emailAddress': 'contact@example.org',
            'role': 'publisher',
            'website': 'https://example.org',
            'contactType': 'organization',
            'address': {'locality': 'Delft', 'country': 'The Netherlands'},
            'phone': '+31-123456789',
            'organization': 'Example Organization',
        },
        'referenceDate': '2026-10-28',
        'referenceSystem': 'https://www.opengis.net/def/crs/EPSG/0/7415',
        'title': 'Example city model',
    }
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'metadata': metadata,
        'CityObjects': {},
        'vertices': [],
    }
    source_path = tmp_path / 'metadata.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    io.write_as_cityjson(city, saved_path)

    assert city.metadata == metadata
    assert json.loads(saved_path.read_text())['metadata'] == metadata


def test_epsg_helpers_read_and_write_reference_system():
    city = City()

    assert city.epsg() is None

    city.set_epsg(7415)

    assert city.epsg() == 7415
    assert city.metadata['referenceSystem'] == 'https://www.opengis.net/def/crs/EPSG/0/7415'


def test_geographical_extent_is_computed_in_real_world_coordinates():
    city = City()
    city.vertices.add([10.125, 20.25, -3.5])
    city.vertices.add([40.5, 50.75, 6.25])

    extent = city.set_geographical_extent()

    assert extent == [10.125, 20.25, -3.5, 40.5, 50.75, 6.25]
    assert city.metadata['geographicalExtent'] == extent


def test_empty_city_has_no_geographical_extent():
    city = City()
    city.metadata['geographicalExtent'] = [0, 0, 0, 1, 1, 1]

    assert city.set_geographical_extent() is None
    assert 'geographicalExtent' not in city.metadata
