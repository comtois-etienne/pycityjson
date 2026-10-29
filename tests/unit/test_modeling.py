import json

import pytest

from pycityjson import io
from pycityjson.model import GeometryPrimitive, MultiLineString, MultiPoint, MultiSurface, Point
from pycityjson.modeling import (
    CityObjectType,
    ModelingProject,
    cuboid,
    elevation_at_coordinate,
    normalize_geometry,
    rectangle,
    rhombicuboctahedron,
)


def test_basic_shapes_are_normalized_and_anchored():
    assert rectangle().get_min_max() == ([-0.5, -0.5, 0.0], [0.5, 0.5, 0.0])
    assert cuboid().get_min_max() == ([-0.5, -0.5, 0.0], [0.5, 0.5, 1.0])
    rbc = rhombicuboctahedron()
    minimum, maximum = rbc.get_min_max()
    assert rbc.surface_count() == 26
    assert minimum == pytest.approx([-0.5, -0.5, 0.0])
    assert maximum == pytest.approx([0.5, 0.5, 1.0])


def test_cuboid_and_rhombicuboctahedron_accept_dimensions():
    assert cuboid(2.0, 3.0, 4.0).get_min_max() == (
        [-1.0, -1.5, 0.0],
        [1.0, 1.5, 4.0],
    )
    minimum, maximum = rhombicuboctahedron(2.0, 3.0, 4.0).get_min_max()
    assert minimum == pytest.approx([-1.0, -1.5, 0.0])
    assert maximum == pytest.approx([1.0, 1.5, 4.0])


def test_solid_shape_dimensions_must_be_positive():
    with pytest.raises(ValueError):
        cuboid(0.0, 1.0, 1.0)
    with pytest.raises(ValueError):
        rhombicuboctahedron(1.0, -1.0, 1.0)


def test_elevation_at_coordinate_averages_nearest_vertices_and_selects_lod():
    project = ModelingProject()
    ground = project.add_object(CityObjectType.GROUND_SURFACE, [0.0, 0.0, 0.0])
    surface = GeometryPrimitive(
        MultiSurface([
            MultiLineString([MultiPoint([
                Point(0, 0, 0), Point(10, 0, 10), Point(0, 10, 0),
            ])]),
        ]),
        lod='2',
    )
    ground.add_geometry(surface, relative=False)

    assert elevation_at_coordinate(ground, (2.0, 3.0)) == pytest.approx(10 / 3)
    assert elevation_at_coordinate(ground, (2.0, 3.0), lod='2') == pytest.approx(10 / 3)


def test_elevation_at_coordinate_uses_distinct_simple_mesh_heights():
    geometry = io.read_wavefront_geometries(
        'tests/test_files/mesh/simple_mesh.obj',
        normalize=(True, True, False),
    )[0]
    project = ModelingProject()
    ground = project.add_object(CityObjectType.GROUND_SURFACE, [0.0, 0.0, 0.0])
    ground.add_geometry(geometry, relative=False)

    elevations = [
        elevation_at_coordinate(ground, (x, y), n=3)
        for x, y in ((0.0, 0.0), (0.25, 0.25), (0.5, 0.5), (0.75, 0.75))
    ]

    assert len(set(elevations)) == len(elevations)


def test_normalize_geometry_supports_actual_corner_anchor():
    geometry = GeometryPrimitive(
        MultiSurface([
            MultiLineString([MultiPoint([
                Point(2, 3, 5), Point(4, 3, 5), Point(4, 5, 5), Point(2, 5, 5),
            ])]),
        ]),
    )
    normalize_geometry(geometry, local_origin='bottom_left_point')
    assert geometry.get_vertices(flatten=True)[0] == pytest.approx([0.0, 0.0, 0.0])
    assert geometry.get_min_max()[1] == pytest.approx([1.0, 1.0, 0.0])


def test_modeling_objects_keep_anchor_geometry_in_sync():
    project = ModelingProject([299052.234, 5036437.132, 23.5], epsg=2950)
    object_ = project.add_object(CityObjectType.BUILDING, [10.0, 20.0, 30.0])
    object_.add_geometry(cuboid())
    object_.translate([1.0, 2.0, 3.0])
    assert object_.anchor == [11.0, 22.0, 33.0]
    assert object_.geometries[0].lod == 'origin'
    assert object_.geometries[0].primitive.get_type() == 'Point'
    assert object_.geometries[0].get_vertices(flatten=True)[0] == pytest.approx([11.0, 22.0, 33.0])
    assert object_.geometries[1].get_vertices(flatten=True)[0] == pytest.approx([10.5, 21.5, 33.0])
    assert project.epsg() == 2950
    assert project.origin == [299052.234, 5036437.132, 23.5]


def test_modeling_objects_support_axis_specific_translations_and_rotations():
    project = ModelingProject()
    object_ = project.add_object(CityObjectType.BUILDING, [0.0, 0.0, 0.0])
    object_.add_geometry(cuboid())

    object_.translate_x(1.0)
    object_.translate_y(2.0)
    object_.translate_z(3.0)
    assert object_.anchor == [1.0, 2.0, 3.0]
    assert object_.geometries[0].get_vertices(flatten=True)[0] == pytest.approx([1.0, 2.0, 3.0])

    object_.rotate_x(90.0)
    object_.rotate_y(90.0)
    object_.rotate_z(90.0)
    assert object_.anchor == [1.0, 2.0, 3.0]


def test_rectangle_accepts_dimensions():
    minimum, maximum = rectangle(10.0, 20.0).get_min_max()
    assert minimum == pytest.approx([-5.0, -10.0, 0.0])
    assert maximum == pytest.approx([5.0, 10.0, 0.0])


def test_trees_can_use_geometry_templates_and_be_materialized():
    project = ModelingProject()
    tree = project.add_object(CityObjectType.SOLITARY_VEGETATION_OBJECT, [10.0, 20.0, 1.5])
    template = rhombicuboctahedron()
    tree.add_geometry(template, use_template=True)
    assert len(project.geometry_templates.geometries) == 1
    assert tree.geometries[1].is_geometry_instance()
    primitive = tree.materialize_geometry(1)
    assert primitive.is_geometry_primitive()
    assert not tree.geometries[1].is_geometry_instance()


def test_geometry_lod_can_be_set_and_changed():
    project = ModelingProject()
    ground = project.add_object(CityObjectType.GROUND_SURFACE, [0.0, 0.0, 0.0])
    ground.add_geometry(cuboid())
    assert ground.geometries[1].lod == '1'
    ground.geometries[1].set_lod(3)
    assert ground.geometries[1].lod == '3'
    ground.set_geometry_lod(1, '4.1')
    assert ground.geometries[1].get_lod() == '4.1'


def test_modeling_project_supports_axis_specific_movement():
    project = ModelingProject()
    object_ = project.add_object(CityObjectType.BUILDING, [0.0, 0.0, 0.0])
    project.move_project_x(1.0)
    project.move_project_y(2.0)
    project.move_project_z(3.0)

    assert project.project_origin == [1.0, 2.0, 3.0]
    assert object_.anchor == [1.0, 2.0, 3.0]


def test_origin_point_is_serialized_and_read_back(tmp_path):
    project = ModelingProject()
    object_ = project.add_object(CityObjectType.BUILDING, [1.0, 2.0, 3.0])
    path = tmp_path / 'origin.city.json'

    io.write_as_cityjson(project, path, purge_vertices=False)
    saved = json.loads(path.read_text())
    origin_geometry = saved['CityObjects'][object_.uuid()]['geometry'][0]
    assert origin_geometry['type'] == 'Point'
    assert origin_geometry['lod'] == 'origin'

    loaded = io.read_cityjson(path)
    loaded_origin = loaded.cityobjects[object_.uuid()].geometries[0]
    assert loaded_origin.primitive.get_type() == 'Point'
    assert loaded_origin.lod == 'origin'
    assert loaded_origin.get_vertices(flatten=True)[0] == pytest.approx([1.0, 2.0, 3.0])
