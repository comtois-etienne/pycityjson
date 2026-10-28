import json

from pycityjson import io
from pycityjson.model import City, Color, Material, Texture


def test_appearance_materials_and_textures_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'CityObjects': {},
        'vertices': [],
        'appearance': {
            'materials': [{
                'name': 'wall',
                'ambientIntensity': 0.2,
                'diffuseColor': [0.9, 0.1, 0.75],
                'emissiveColor': [0.1, 0.2, 0.3],
                'specularColor': [0.8, 0.7, 0.6],
                'shininess': 0.2,
                'transparency': 0.5,
                'isSmooth': True,
            }],
            'textures': [{
                'type': 'PNG',
                'image': 'appearances/wall.png',
                'wrapMode': 'mirror',
                'textureType': 'specific',
                'borderColor': [0.0, 0.1, 0.2, 1.0],
            }],
            'vertices-texture': [[0.0, 0.0], [1.0, 1.0]],
            'default-theme-texture': 'summer',
            'default-theme-material': 'visual',
        },
    }
    source_path = tmp_path / 'appearance.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    material = city.materials[0]
    texture = city.textures[0]

    assert material.name == 'wall'
    assert material.diffuseColor == Color(0.9, 0.1, 0.75)
    assert material.isSmooth is True
    assert texture == Texture(
        'PNG',
        'appearances/wall.png',
        'mirror',
        'specific',
        Color(0.0, 0.1, 0.2, 1.0),
    )
    assert city.texture_vertices == source['appearance']['vertices-texture']
    assert city.default_theme_texture == 'summer'
    assert city.default_theme_material == 'visual'

    io.write_as_cityjson(city, saved_path)
    assert json.loads(saved_path.read_text())['appearance'] == source['appearance']


def test_geometry_texture_assignments_round_trip(tmp_path):
    source = {
        'type': 'CityJSON',
        'version': '2.0',
        'transform': {'scale': [1, 1, 1], 'translate': [0, 0, 0]},
        'vertices': [[0, 0, 0], [1, 0, 0], [0, 1, 0]],
        'appearance': {
            'textures': [{'type': 'JPG', 'image': 'roof.jpg'}],
            'vertices-texture': [[0, 0], [1, 0], [0, 1]],
        },
        'CityObjects': {
            'roof': {
                'type': 'GenericCityObject',
                'geometry': [{
                    'type': 'MultiSurface',
                    'lod': '2',
                    'boundaries': [[[0, 1, 2]]],
                    'texture': {
                        'roof-theme': {'values': [[[0, 0, 1, 2]]]},
                    },
                }],
            },
        },
    }
    source_path = tmp_path / 'texture.city.json'
    saved_path = tmp_path / 'saved.city.json'
    source_path.write_text(json.dumps(source))

    city = io.read_cityjson(source_path)
    io.write_as_cityjson(city, saved_path)
    saved = json.loads(saved_path.read_text())

    assert saved['appearance'] == source['appearance']
    assert saved['CityObjects']['roof']['geometry'][0]['texture'] == (
        source['CityObjects']['roof']['geometry'][0]['texture']
    )
