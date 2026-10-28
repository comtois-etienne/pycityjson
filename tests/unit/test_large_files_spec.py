import json

import pytest

from pycityjson import io


def test_cityjson_feature_stream_is_read_lazily(tmp_path):
    path = tmp_path / 'city.city.jsonl'
    entries = [
        {
            'type': 'CityJSON',
            'version': '2.0',
            'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
            'CityObjects': {},
            'vertices': [],
        },
        {
            'type': 'CityJSONFeature',
            'id': 'building-a',
            'CityObjects': {'building-a': {'type': 'Building'}},
            'vertices': [],
        },
        {
            'type': 'CityJSONFeature',
            'id': 'building-b',
            'CityObjects': {'building-b': {'type': 'Building'}},
            'vertices': [],
        },
    ]
    path.write_text('\n'.join(json.dumps(entry) for entry in entries))

    stream = io.read_cityjson_features(path)

    assert next(stream) == entries[0]
    assert next(stream) == entries[1]
    assert next(stream) == entries[2]
    with pytest.raises(StopIteration):
        next(stream)


def test_cityjson_feature_stream_allows_appearance_but_forbids_global_members(tmp_path):
    path = tmp_path / 'city.city.jsonl'
    path.write_text(
        '\n'.join([
            json.dumps({
                'type': 'CityJSON',
                'version': '2.0',
                'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
                'CityObjects': {},
                'vertices': [],
            }),
            json.dumps({
                'type': 'CityJSONFeature',
                'id': 'feature-1',
                'CityObjects': {},
                'vertices': [],
                'appearance': {},
            }),
        ]),
    )

    assert list(io.read_cityjson_features(path))[-1]['id'] == 'feature-1'

    path.write_text(
        '\n'.join([
            json.dumps({
                'type': 'CityJSON',
                'version': '2.0',
                'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
                'CityObjects': {},
                'vertices': [],
            }),
            json.dumps({
                'type': 'CityJSONFeature',
                'id': 'feature-1',
                'CityObjects': {},
                'vertices': [],
                'transform': {},
            }),
        ]),
    )
    with pytest.raises(ValueError, match='forbidden members'):
        list(io.read_cityjson_features(path))


@pytest.mark.parametrize(
    'feature',
    [
        {'type': 'CityJSONFeature', 'CityObjects': {}, 'vertices': []},
        {'type': 'CityJSONFeature', 'id': 'x', 'vertices': []},
        {'type': 'CityJSONFeature', 'id': 'x', 'CityObjects': {}},
    ],
)
def test_cityjson_feature_stream_rejects_incomplete_features(tmp_path, feature):
    path = tmp_path / 'city.city.jsonl'
    header = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'CityObjects': {},
        'vertices': [],
    }
    path.write_text(f'{json.dumps(header)}\n{json.dumps(feature)}\n')

    with pytest.raises(ValueError, match='missing required members'):
        list(io.read_cityjson_features(path))
