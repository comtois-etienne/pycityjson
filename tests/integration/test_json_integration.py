import json
from dataclasses import dataclass
from typing import TextIO

from pytest_unordered import unordered

from pycityjson import io, model


class TestJsonIntegration:
    def test_transform_all_geometries_primitive(self, file_manager):
        """
         Test that calling transform on a CityObject with multiple primitive geometries
         transforms all geometries.

         Before:
            +--------------------+
           /         /          /|
          /         /          / |
         +--------------------+  |
         |         |          |  |
         |         |          |  +
         |         |          | /
         |         |          |/
         +---------+----------+

         After:

                    +--------+
                   /        /|
                  /        / |
                 +--------+  |
                 |        |  |
           +-----|        |  +
          /      |        | /
         /       |        |/
        +--------+--------+
        |        |   |
        |        |   +
        |        |  /
        |        | /
        +--------+
        """
        # Arrange
        cityjson = {
            'type': 'CityJSON',
            'version': '2.0',
            'CityObjects': {
                'id-1': {
                    'type': 'GenericCityObject',
                    'attributes': {
                        'function': 'something',
                        'uuid': 'id-1',
                    },
                    'geometry': [
                        {
                            'type': 'Solid',
                            'lod': '1',
                            'boundaries': [
                                [
                                    [
                                        [
                                            0,
                                            1,
                                            2,
                                            3,
                                        ],
                                    ],
                                    [
                                        [
                                            4,
                                            5,
                                            1,
                                            0,
                                        ],
                                    ],
                                    [
                                        [
                                            5,
                                            6,
                                            2,
                                            1,
                                        ],
                                    ],
                                    [
                                        [
                                            6,
                                            7,
                                            3,
                                            2,
                                        ],
                                    ],
                                    [
                                        [
                                            7,
                                            4,
                                            0,
                                            3,
                                        ],
                                    ],
                                    [
                                        [
                                            7,
                                            6,
                                            5,
                                            4,
                                        ],
                                    ],
                                ],
                            ],
                        },
                    ],
                },
                'id-2': {
                    'type': 'GenericCityObject',
                    'attributes': {
                        'function': 'something',
                        'uuid': 'id-2',
                    },
                    'geometry': [
                        {
                            'type': 'Solid',
                            'lod': '1',
                            'boundaries': [
                                [
                                    [
                                        [
                                            1,
                                            8,
                                            9,
                                            2,
                                        ],
                                    ],
                                    [
                                        [
                                            5,
                                            10,
                                            8,
                                            1,
                                        ],
                                    ],
                                    [
                                        [
                                            10,
                                            11,
                                            9,
                                            8,
                                        ],
                                    ],
                                    [
                                        [
                                            11,
                                            6,
                                            2,
                                            9,
                                        ],
                                    ],
                                    [
                                        [
                                            6,
                                            5,
                                            1,
                                            2,
                                        ],
                                    ],
                                    [
                                        [
                                            6,
                                            11,
                                            10,
                                            5,
                                        ],
                                    ],
                                ],
                            ],
                        },
                        {
                            'type': 'Solid',
                            'lod': '1',
                            'boundaries': [
                                [
                                    [
                                        [
                                            1,
                                            8,
                                            9,
                                            2,
                                        ],
                                    ],
                                    [
                                        [
                                            5,
                                            10,
                                            8,
                                            1,
                                        ],
                                    ],
                                    [
                                        [
                                            10,
                                            11,
                                            9,
                                            8,
                                        ],
                                    ],
                                    [
                                        [
                                            11,
                                            6,
                                            2,
                                            9,
                                        ],
                                    ],
                                    [
                                        [
                                            6,
                                            5,
                                            1,
                                            2,
                                        ],
                                    ],
                                    [
                                        [
                                            6,
                                            11,
                                            10,
                                            5,
                                        ],
                                    ],
                                ],
                            ],
                        },
                    ],
                },
            },
            'transform': {
                'scale': [
                    0.001,
                    0.001,
                    0.001,
                ],
                'translate': [
                    299151.825,
                    5035820.421,
                    12.005,
                ],
            },
            'vertices': [
                [
                    0,
                    0,
                    10000,
                ],
                [
                    10000,
                    0,
                    10000,
                ],
                [
                    10000,
                    10000,
                    10000,
                ],
                [
                    0,
                    10000,
                    10000,
                ],
                [
                    0,
                    0,
                    0,
                ],
                [
                    10000,
                    0,
                    0,
                ],
                [
                    10000,
                    10000,
                    0,
                ],
                [
                    0,
                    10000,
                    0,
                ],
                [
                    20000,
                    0,
                    10000,
                ],
                [
                    20000,
                    10000,
                    10000,
                ],
                [
                    20000,
                    0,
                    0,
                ],
                [
                    20000,
                    10000,
                    0,
                ],
            ],
            'metadata': {
                'geographicalExtent': [
                    299151.825,
                    5035820.421,
                    12.005,
                    299171.825,
                    5035830.421,
                    22.005,
                ],
            },
        }
        file_path = file_manager.save_json(cityjson)
        saved_file_path = file_manager.get_empty_file_path()
        transformation_matrix = model.TransformationMatrix().translate(
            model.Vector(z=10),
        )

        # Act
        city = io.read(file_path)
        city.cityobjects['id-2'].transform(transformation_matrix)  # Should transform all geometries
        io.write_as_cityjson(city, saved_file_path)

        # Assert
        loaded_result = json.load(open(saved_file_path))
        assert len(loaded_result['vertices']) == 14

        def _get_index(x: float, y: float, z: float) -> int:
            for i, v in enumerate(loaded_result['vertices']):
                if v[0] == x and v[1] == y and v[2] == z:
                    return i

            raise ValueError(f'Vertex {x}, {y}, {z} not found')

        i_0_0_0 = _get_index(0, 0, 0)
        i_0_10_0 = _get_index(0, 10_000, 0)
        i_0_0_10 = _get_index(0, 0, 10_000)
        i_0_10_10 = _get_index(0, 10_000, 10_000)

        i_10_0_0 = _get_index(10_000, 0, 0)
        i_10_10_0 = _get_index(10_000, 10_000, 0)
        i_10_0_10 = _get_index(10_000, 0, 10_000)
        i_10_10_10 = _get_index(10_000, 10_000, 10_000)
        i_10_0_20 = _get_index(10_000, 0, 20_000)
        i_10_10_20 = _get_index(10_000, 10_000, 20_000)

        i_20_0_10 = _get_index(20_000, 0, 10_000)
        i_20_10_10 = _get_index(20_000, 10_000, 10_000)
        i_20_0_20 = _get_index(20_000, 0, 20_000)
        i_20_10_20 = _get_index(20_000, 10_000, 20_000)

        cube_1_faces = [
            unordered(
                [unordered([i_0_0_0, i_10_0_0, i_10_0_10, i_0_0_10])],  # 1
                [unordered([i_10_0_0, i_10_10_0, i_10_10_10, i_10_0_10])],  # 2
                [unordered([i_0_0_10, i_10_0_10, i_10_10_10, i_0_10_10])],  # 3
                [unordered([i_0_0_0, i_10_0_0, i_10_10_0, i_0_10_0])],  # 4
                [unordered([i_0_0_0, i_0_0_10, i_0_10_10, i_0_10_0])],  # 5
                [unordered([i_0_10_0, i_10_10_0, i_10_10_10, i_0_10_10])],  # 6
            )
        ]

        cube_2_faces = [
            unordered(
                [unordered([i_10_0_10, i_20_0_10, i_20_0_20, i_10_0_20])],  # 1
                [unordered([i_20_0_10, i_20_10_10, i_20_10_20, i_20_0_20])],  # 2
                [unordered([i_10_0_20, i_20_0_20, i_20_10_20, i_10_10_20])],  # 3
                [unordered([i_10_0_10, i_20_0_10, i_20_10_10, i_10_10_10])],  # 4
                [unordered([i_10_0_10, i_10_0_20, i_10_10_20, i_10_10_10])],  # 5
                [unordered([i_10_10_10, i_20_10_10, i_20_10_20, i_10_10_20])],  # 6
            )
        ]

        assert loaded_result['CityObjects']['id-1']['geometry'][0]['boundaries'] == cube_1_faces
        assert loaded_result['CityObjects']['id-2']['geometry'][0]['boundaries'] == cube_2_faces
        assert loaded_result['CityObjects']['id-2']['geometry'][1]['boundaries'] == cube_2_faces

    def test_transform_all_geometries_mixed(self, file_manager):
        """
         Test that calling transform on a CityObject with multiple (primitive/templates) geometries
         transforms all geometries.

         The primitives should be transformed however only the origin of the templates should be transformed.

         Before:
            +--------------------+
           /         /          /|
          /         /          / |
         +--------------------+  |
         |         |          |  |
         |         |          |  +
         |         |          | /
         |         |          |/
         +---------+----------+

         After:

                    +--------+
                   /        /|
                  /        / |
                 +--------+  |
                 |        |  |
           +-----|        |  +
          /      |        | /
         /       |        |/
        +--------+--------+
        |        |   |
        |        |   +
        |        |  /
        |        | /
        +--------+
        """
        # Arrange
        cityjson = {
            'type': 'CityJSON',
            'version': '2.0',
            'CityObjects': {
                'id-1': {
                    'type': 'GenericCityObject',
                    'attributes': {
                        'function': 'something',
                        'uuid': 'id-1',
                    },
                    'geometry': [
                        {
                            'type': 'Solid',
                            'lod': '1',
                            'boundaries': [
                                [
                                    [
                                        [
                                            0,
                                            1,
                                            2,
                                            3,
                                        ],
                                    ],
                                    [
                                        [
                                            4,
                                            5,
                                            1,
                                            0,
                                        ],
                                    ],
                                    [
                                        [
                                            5,
                                            6,
                                            2,
                                            1,
                                        ],
                                    ],
                                    [
                                        [
                                            6,
                                            7,
                                            3,
                                            2,
                                        ],
                                    ],
                                    [
                                        [
                                            7,
                                            4,
                                            0,
                                            3,
                                        ],
                                    ],
                                    [
                                        [
                                            7,
                                            6,
                                            5,
                                            4,
                                        ],
                                    ],
                                ],
                            ],
                        },
                    ],
                },
                'id-2': {
                    'type': 'GenericCityObject',
                    'attributes': {
                        'function': 'something',
                        'uuid': 'id-2',
                    },
                    'geometry': [
                        {
                            'type': 'Solid',
                            'lod': '2',
                            'boundaries': [
                                [
                                    [
                                        [
                                            1,
                                            8,
                                            9,
                                            2,
                                        ],
                                    ],
                                    [
                                        [
                                            5,
                                            10,
                                            8,
                                            1,
                                        ],
                                    ],
                                    [
                                        [
                                            10,
                                            11,
                                            9,
                                            8,
                                        ],
                                    ],
                                    [
                                        [
                                            11,
                                            6,
                                            2,
                                            9,
                                        ],
                                    ],
                                    [
                                        [
                                            6,
                                            5,
                                            1,
                                            2,
                                        ],
                                    ],
                                    [
                                        [
                                            6,
                                            11,
                                            10,
                                            5,
                                        ],
                                    ],
                                ],
                            ],
                        },
                        {
                            'type': 'GeometryInstance',
                            'template': 0,
                            'boundaries': [
                                5,
                            ],
                            'transformationMatrix': [
                                10,
                                0,
                                0,
                                0,
                                0,
                                10,
                                0,
                                0,
                                0,
                                0,
                                10,
                                0,
                                0,
                                0,
                                0,
                                1,
                            ],
                        },
                    ],
                },
            },
            'transform': {
                'scale': [
                    0.001,
                    0.001,
                    0.001,
                ],
                'translate': [
                    299151.825,
                    5035820.421,
                    12.005,
                ],
            },
            'vertices': [
                [
                    0,
                    0,
                    10000,
                ],
                [
                    10000,
                    0,
                    10000,
                ],
                [
                    10000,
                    10000,
                    10000,
                ],
                [
                    0,
                    10000,
                    10000,
                ],
                [
                    0,
                    0,
                    0,
                ],
                [
                    10000,
                    0,
                    0,
                ],
                [
                    10000,
                    10000,
                    0,
                ],
                [
                    0,
                    10000,
                    0,
                ],
                [
                    20000,
                    0,
                    10000,
                ],
                [
                    20000,
                    10000,
                    10000,
                ],
                [
                    20000,
                    0,
                    0,
                ],
                [
                    20000,
                    10000,
                    0,
                ],
            ],
            'geometry-templates': {
                'vertices-templates': [
                    [
                        0,
                        0,
                        0,
                    ],
                    [
                        1,
                        0,
                        0,
                    ],
                    [
                        0,
                        1,
                        0,
                    ],
                    [
                        1,
                        1,
                        0,
                    ],
                    [
                        0,
                        0,
                        1,
                    ],
                    [
                        1,
                        0,
                        1,
                    ],
                    [
                        0,
                        1,
                        1,
                    ],
                    [
                        1,
                        1,
                        1,
                    ],
                ],
                'templates': [
                    {
                        'boundaries': [
                            [
                                [
                                    0,
                                    1,
                                    3,
                                    2,
                                ],
                            ],
                            [
                                [
                                    4,
                                    5,
                                    1,
                                    0,
                                ],
                            ],
                            [
                                [
                                    5,
                                    4,
                                    6,
                                    7,
                                ],
                            ],
                            [
                                [
                                    7,
                                    6,
                                    2,
                                    3,
                                ],
                            ],
                            [
                                [
                                    7,
                                    3,
                                    1,
                                    5,
                                ],
                            ],
                            [
                                [
                                    6,
                                    4,
                                    0,
                                    2,
                                ],
                            ],
                        ],
                        'lod': '1',
                        'type': 'MultiSurface',
                    },
                ],
            },
            'metadata': {
                'geographicalExtent': [
                    299151.825,
                    5035820.421,
                    12.005,
                    299171.825,
                    5035830.421,
                    22.005,
                ],
            },
        }
        file_path = file_manager.save_json(cityjson)
        saved_file_path = file_manager.get_empty_file_path()
        transformation_matrix = model.TransformationMatrix().translate(
            model.Vector(z=12),
        )

        # Act
        city = io.read(file_path)
        city.cityobjects['id-2'].transform(transformation_matrix)  # Should transform all geometries
        io.write_as_cityjson(city, saved_file_path)

        # Assert
        loaded_result = json.load(open(saved_file_path))
        assert len(loaded_result['vertices']) == 14

        def _get_index(x: float, y: float, z: float) -> int:
            for i, v in enumerate(loaded_result['vertices']):
                if v[0] == x and v[1] == y and v[2] == z:
                    return i

            raise ValueError(f'Vertex {x}, {y}, {z} not found')

        i_0_0_0 = _get_index(0, 0, 0)
        i_0_10_0 = _get_index(0, 10_000, 0)
        i_0_0_10 = _get_index(0, 0, 10_000)
        i_0_10_10 = _get_index(0, 10_000, 10_000)

        i_10_0_0 = _get_index(10_000, 0, 0)
        i_10_10_0 = _get_index(10_000, 10_000, 0)
        i_10_0_10 = _get_index(10_000, 0, 10_000)
        i_10_10_10 = _get_index(10_000, 10_000, 10_000)
        i_10_0_20 = _get_index(10_000, 0, 20_000)
        i_10_10_20 = _get_index(10_000, 10_000, 20_000)

        i_20_0_10 = _get_index(20_000, 0, 10_000)
        i_20_10_10 = _get_index(20_000, 10_000, 10_000)
        i_20_0_20 = _get_index(20_000, 0, 20_000)
        i_20_10_20 = _get_index(20_000, 10_000, 20_000)

        cube_1_faces = [
            unordered(
                [unordered([i_0_0_0, i_10_0_0, i_10_0_10, i_0_0_10])],  # 1
                [unordered([i_10_0_0, i_10_10_0, i_10_10_10, i_10_0_10])],  # 2
                [unordered([i_0_0_10, i_10_0_10, i_10_10_10, i_0_10_10])],  # 3
                [unordered([i_0_0_0, i_10_0_0, i_10_10_0, i_0_10_0])],  # 4
                [unordered([i_0_0_0, i_0_0_10, i_0_10_10, i_0_10_0])],  # 5
                [unordered([i_0_10_0, i_10_10_0, i_10_10_10, i_0_10_10])],  # 6
            )
        ]

        cube_2_faces = [
            unordered(
                [unordered([i_10_0_10, i_20_0_10, i_20_0_20, i_10_0_20])],  # 1
                [unordered([i_20_0_10, i_20_10_10, i_20_10_20, i_20_0_20])],  # 2
                [unordered([i_10_0_20, i_20_0_20, i_20_10_20, i_10_10_20])],  # 3
                [unordered([i_10_0_10, i_20_0_10, i_20_10_10, i_10_10_10])],  # 4
                [unordered([i_10_0_10, i_10_0_20, i_10_10_20, i_10_10_10])],  # 5
                [unordered([i_10_10_10, i_20_10_10, i_20_10_20, i_10_10_20])],  # 6
            )
        ]
        primitive_geometry = next(filter(lambda g: g['type'] != 'GeometryInstance', loaded_result['CityObjects']['id-2']['geometry']))
        instance_geometry = next(filter(lambda g: g['type'] == 'GeometryInstance', loaded_result['CityObjects']['id-2']['geometry']))

        assert loaded_result['CityObjects']['id-1']['geometry'][0]['boundaries'] == cube_1_faces

        assert primitive_geometry['boundaries'] == cube_2_faces
        assert instance_geometry['boundaries'] == [i_10_0_10]
