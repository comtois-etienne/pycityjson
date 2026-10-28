import pytest

from pycityjson.model import Vertices


def test_vertices_rounds_and_deduplicates_vertices():
    vertices = Vertices(
        [
            [1.2349, 2.3451, 3.4567],
            [1.2351, 2.3454, 3.4566],
        ],
        precision=3,
    )

    assert len(vertices) == 1
    assert vertices.tolist() == [[1.235, 2.345, 3.457]]


def test_vertices_supports_index_and_vertex_lookup_with_start_index():
    vertices = Vertices([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]], start_index=10)

    assert vertices[10] == [0.0, 1.0, 2.0]
    assert vertices[11] == [3.0, 4.0, 5.0]
    assert vertices[[3.0, 4.0, 5.0]] == 11
    assert vertices[9] is None
    assert vertices[12] is None
    assert vertices[[6.0, 7.0, 8.0]] is None


def test_vertices_can_be_iterated_and_checked_for_containment():
    vertices = Vertices([[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]])

    assert list(vertices) == [[0.0, 1.0, 2.0], [3.0, 4.0, 5.0]]
    assert [0.0, 1.0, 2.0] in vertices
    assert [6.0, 7.0, 8.0] not in vertices


def test_vertices_provide_axis_values_and_bounds():
    vertices = Vertices([[3.0, 2.0, 9.0], [1.0, 8.0, 4.0], [5.0, 0.0, 6.0]])

    assert vertices.get_axis(0) == [3.0, 1.0, 5.0]
    assert vertices.get_axis(1) == [2.0, 8.0, 0.0]
    assert vertices.get_axis(2) == [9.0, 4.0, 6.0]
    assert vertices.get_min() == [1.0, 0.0, 4.0]
    assert vertices.get_max() == [5.0, 8.0, 9.0]


def test_vertices_return_copies_from_index_and_list_conversion():
    vertices = Vertices([[1.0, 2.0, 3.0]])

    vertex = vertices[0]
    listed = vertices.tolist()
    vertex[0] = 100.0
    listed[0][1] = 200.0

    assert vertices[0] == [1.0, 2.0, 3.0]


@pytest.mark.parametrize('axis', [3])
def test_vertices_reject_invalid_axis(axis):
    vertices = Vertices([[1.0, 2.0, 3.0]])

    with pytest.raises(IndexError):
        vertices.get_axis(axis)
