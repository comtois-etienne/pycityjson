from dataclasses import FrozenInstanceError

import pytest

from pycityjson.model import TransformationMatrix, Vector


def test_vector_converts_to_a_vertex():
    assert Vector(1, 2, 3).tolist() == [1, 2, 3]
    assert Vector().tolist() == [0.0, 0.0, 0.0]


def test_identity_matrix_reprojects_vertices_unchanged():
    matrix = TransformationMatrix()

    assert matrix.tolist() == [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    assert matrix.get_origin() == [0, 0, 0]
    assert matrix.reproject_vertex([1, 2, 3]) == [1.0, 2.0, 3.0]


def test_translation_accepts_vertices_and_vectors():
    matrix = TransformationMatrix().translate([1, 2, 3])
    translated = matrix.translate(Vector(x=4, y=5, z=6))

    assert matrix.get_origin() == [1, 2, 3]
    assert translated.get_origin() == [5, 7, 9]
    assert translated.reproject_vertex([1, 1, 1]) == [6.0, 8.0, 10.0]


def test_scaling_reprojects_vertices_without_mutating_the_original():
    matrix = TransformationMatrix().scale(Vector(x=2, y=3, z=4))

    assert matrix.reproject_vertex([1, 1, 1]) == [2.0, 3.0, 4.0]
    assert TransformationMatrix().reproject_vertex([1, 1, 1]) == [1.0, 1.0, 1.0]


def test_recenter_removes_translation():
    matrix = TransformationMatrix().translate([10, 20, 30]).recenter()

    assert matrix.get_origin() == [0, 0, 0]
    assert matrix.reproject_vertex([1, 2, 3]) == [1.0, 2.0, 3.0]


@pytest.mark.parametrize(
    ('rotation', 'vertex', 'expected'),
    [
        ('rotate_x', [0, 1, 0], [0.0, 0.0, -1.0]),
        ('rotate_y', [1, 0, 0], [0.0, 0.0, 1.0]),
        ('rotate_z', [1, 0, 0], [0.0, -1.0, 0.0]),
    ],
)
def test_rotations_reproject_vertices(rotation, vertex, expected):
    matrix = getattr(TransformationMatrix(), rotation)(90)

    assert matrix.reproject_vertex(vertex) == pytest.approx(expected)


def test_reproject_vertices_preserves_nested_structure():
    matrix = TransformationMatrix().translate([1, 2, 3])

    assert matrix.reproject_vertices([[[0, 0, 0], [1, 1, 1]]]) == [
        [[1.0, 2.0, 3.0], [2.0, 3.0, 4.0]],
    ]


def test_dot_composes_transformations():
    matrix = TransformationMatrix().translate([10, 20, 30])
    rotation = TransformationMatrix().rotate_z(90, from_origin=True)

    composed = matrix.dot(rotation, from_origin=True)

    assert composed.reproject_vertex([1, 0, 0]) == pytest.approx([20.0, -11.0, 30.0])


def test_matrix_is_immutable_and_copy_is_independent():
    matrix = TransformationMatrix().translate([1, 2, 3])
    copied = matrix.copy()
    values = copied.tolist()
    values[3] = 100

    assert matrix.get_origin() == [1, 2, 3]
    assert copied.get_origin() == [1, 2, 3]
    with pytest.raises(FrozenInstanceError):
        matrix._TransformationMatrix__matrix = []
