import json

from pycityjson import io
from pycityjson.model import City


def test_write_cityjson_without_pretty_printing_uses_compact_separators(tmp_path):
    path = tmp_path / 'compact.city.json'
    city = City()
    city.metadata = {
        'description': 'value with commas, colons: and ": " text',
        'nested': {'items': ['a,b', 'c:d']},
    }

    io.write_as_cityjson(city, path, pretty=False)

    content = path.read_text()
    expected = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [0.001, 0.001, 0.001], 'translate': [0, 0, 0]},
        'CityObjects': {},
        'vertices': [],
        'extensions': {},
        'metadata': city.metadata,
    }
    assert content == json.dumps(expected, separators=(',', ':'))
    assert json.loads(content) == expected


def test_write_cityjson_preserves_delimiters_inside_metadata_strings(tmp_path):
    path = tmp_path / 'metadata.city.json'
    city = City()
    city.metadata = {
        'text': 'not an injection: , : "quoted" and } ]',
    }

    io.write_as_cityjson(city, path, pretty=False)

    saved = json.loads(path.read_text())
    assert saved['metadata'] == city.metadata


def test_write_cityjson_with_pretty_printing_keeps_readable_format(tmp_path):
    path = tmp_path / 'pretty.city.json'

    io.write_as_cityjson(City(), path, pretty=True)

    content = path.read_text()
    assert ': ' in content
