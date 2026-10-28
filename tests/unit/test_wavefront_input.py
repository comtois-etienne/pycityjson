from pathlib import Path

from pycityjson import io

SOLIDS = Path('tests/test_files/solids')


def test_read_wavefront_imports_objects_geometry_lods_and_materials():
    city = io.read_wavefront(SOLIDS / 'solids.obj')

    objects = city.cityobjects.tolist()
    assert len(objects) == 4
    assert [object_.uuid() for object_ in objects] == [
        'Tetrahedron',
        'Hexahedron',
        'Octahedron',
        'Dodecahedron_and_Icosahedron',
    ]
    assert [object_.type for object_ in objects] == [
        'GenericCityObject',
        'SolitaryVegetationObject',
        'GenericCityObject',
        'Building',
    ]
    assert [object_.geometries[0].lod for object_ in objects[:3]] == ['2', '3', '2']
    assert [geometry.lod for geometry in objects[3].geometries] == ['3', '2']
    geometries = [object_.geometries[0] for object_ in objects[:3]] + objects[3].geometries
    assert [len(geometry.primitive.get_surfaces()) for geometry in geometries] == [
        4, 6, 8, 12, 20,
    ]
    assert len(city.vertices) == 50
    assert city.materials['Red'].diffuseColor.to_list() == [0.8, 0.2, 0.2]


def test_read_wavefront_uses_object_type_and_group_as_lod(tmp_path):
    obj = tmp_path / 'model.obj'
    mtl = tmp_path / 'model.mtl'
    mtl.write_text('newmtl Blue\nKd 0.0 0.0 1.0\n')
    obj.write_text(
        'mtllib model.mtl\n'
        'o object-1 Building\n'
        'g lod_2\n'
        'usemtl Blue\n'
        'v 0 0 0\n'
        'v 1 0 0\n'
        'v 0 1 0\n'
        'f 1/1 2/2 3/3\n',
    )

    city = io.read_wavefront(obj)
    city_object = city.cityobjects['object-1']

    assert city_object.type == 'Building'
    assert [geometry.lod for geometry in city_object.geometries] == ['2']
    assert city_object.geometries[0].get_surfaces()[0].get_material().name == 'Blue'


def test_read_wavefront_uses_function_defaults_for_groups_without_lod(tmp_path):
    obj = tmp_path / 'model.obj'
    obj.write_text(
        'g roof\n'
        'v 0 0 0\n'
        'v 1 0 0\n'
        'v 0 1 0\n'
        'f 1 2 3\n',
    )

    city = io.read_wavefront(obj, lod=3, type='Railway', add_uuid=False)
    city_object = city.cityobjects['obj-1']

    assert city_object.type == 'Railway'
    assert city_object.geometries[0].lod == '3'
    assert city_object.uuid() == 'obj-1'


def test_read_wavefront_supports_explicit_material_path_and_negative_indices(tmp_path):
    obj = tmp_path / 'model.obj'
    mtl = tmp_path / 'materials.mtl'
    mtl.write_text('newmtl Red\nKd 1 0 0\n')
    obj.write_text(
        'o object-1\n'
        'g 1\n'
        'usemtl Red\n'
        'v 0 0 0\n'
        'v 1 0 0\n'
        'v 0 1 0\n'
        'f -3 -2 -1\n',
    )

    city = io.read_wavefront(obj, mtl)

    assert city.cityobjects['object-1'].type == 'GenericCityObject'
    assert city.cityobjects['object-1'].geometries[0].lod == '1'
    assert city.cityobjects['object-1'].get_vertices(flatten=True) == [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
