import pytest

from pycityjson.model import (
    GeometryInstance,
    GeometryPrimitive,
    MultiLineString,
    MultiPoint,
    MultiSurface,
    Point,
    TransformationMatrix,
)


def _surface() -> MultiLineString:
    return MultiLineString(
        [
            MultiPoint(
                [
                    Point(0, 0, 0),
                    Point(2, 0, 0),
                    Point(2, 4, 2),
                ],
            ),
        ],
    )


def _geometry() -> GeometryPrimitive:
    return GeometryPrimitive(MultiSurface([_surface()]), lod='2')


def test_geometry_primitive_exposes_geometry_properties():
    geometry = _geometry()

    assert str(geometry) == 'GeometryMultiSurface(lod=2)'
    assert geometry.get_lod() == '2'
    assert geometry.is_geometry_primitive()
    assert not geometry.is_geometry_instance()
    assert geometry.get_vertices(flatten=True) == [[0, 0, 0], [2, 0, 0], [2, 4, 2]]
    assert geometry.get_min_max() == ([0, 0, 0], [2, 4, 2])
    assert geometry.get_origin() == [1.0, 2.0, 0]
    assert geometry.surface_count() == 1
    assert len(geometry.get_surfaces()) == 1
    assert geometry.get_surfaces()[0].get_vertices(flatten=True) == _surface().get_vertices(flatten=True)


def test_geometry_primitive_transforms_around_its_base_center():
    geometry = _geometry()

    geometry.transform(TransformationMatrix().scale([2, 2, 2]))

    assert geometry.get_vertices(flatten=True) == [[-1.0, -2.0, 0.0], [3.0, -2.0, 0.0], [3.0, 6.0, 4.0]]


def test_geometry_primitive_duplicate_is_independent():
    geometry = _geometry()
    duplicate = geometry.duplicate()

    duplicate.transform(TransformationMatrix().translate([1, 2, 3]), center=[0, 0, 0])

    assert geometry.get_vertices(flatten=True) == [[0, 0, 0], [2, 0, 0], [2, 4, 2]]
    assert duplicate.get_vertices(flatten=True) == [[1, 2, 3], [3, 2, 3], [3, 6, 5]]
    assert duplicate != geometry
    assert duplicate.duplicate().get_vertices(flatten=True) == duplicate.get_vertices(flatten=True)


def test_geometry_instance_reprojects_template_vertices_and_can_be_converted():
    template = _geometry()
    instance = GeometryInstance(template, TransformationMatrix().translate([10, 20, 30]))

    assert instance.get_lod() == '2'
    assert instance.get_origin() == [10, 20, 30]
    assert instance.get_vertices(flatten=True) == [[10.0, 20.0, 30.0], [12.0, 20.0, 30.0], [12.0, 24.0, 32.0]]
    assert instance.get_min_max() == ([10.0, 20.0, 30.0], [12.0, 24.0, 32.0])
    assert instance.surface_count() == 1
    assert instance.get_surfaces() == template.get_surfaces()

    converted = instance.to_geometry_primitive()
    assert converted.get_vertices(flatten=True) == instance.get_vertices(flatten=True)
    assert converted.get_lod() == '2'


def test_geometry_instance_duplicate_shares_template_but_copies_matrix():
    template = _geometry()
    instance = GeometryInstance(template, TransformationMatrix().translate([1, 2, 3]))
    duplicate = instance.duplicate()

    duplicate.transform(TransformationMatrix().translate([4, 5, 6]))

    assert duplicate.geometry is template
    assert instance.get_origin() == [1, 2, 3]
    assert duplicate.get_origin() == [5, 7, 9]


@pytest.mark.parametrize(
    ('geometry', 'primitive', 'instance'),
    [
        (_geometry(), True, False),
        (GeometryInstance(_geometry(), TransformationMatrix()), False, True),
    ],
)
def test_geometry_type_helpers(geometry, primitive, instance):
    assert geometry.is_geometry_primitive() is primitive
    assert geometry.is_geometry_instance() is instance
