"""Normalized geometry factories for common procedural shapes."""

from itertools import permutations, product

import numpy as np

from pycityjson.model import GeometryPrimitive, MultiLineString, MultiPoint, MultiSurface, Point, Solid

from .geometry import normalize_geometry


def rectangle(x: float = 1.0, y: float = 1.0) -> GeometryPrimitive:
    """Create an XY rectangle with dimensions ``x`` and ``y``."""
    if x <= 0 or y <= 0:
        raise ValueError('Rectangle dimensions must be positive')
    return _surface_geometry(
        [[-x / 2, -y / 2, 0], [x / 2, -y / 2, 0], [x / 2, y / 2, 0], [-x / 2, y / 2, 0]],
        None,
    )


def cuboid(x: float = 1.0, y: float = 1.0, z: float = 1.0) -> GeometryPrimitive:
    """Create a cuboid with dimensions ``x``, ``y``, and ``z``."""
    _validate_dimensions(x, y, z)
    vertices = [
        [-x / 2, -y / 2, 0], [x / 2, -y / 2, 0], [x / 2, y / 2, 0], [-x / 2, y / 2, 0],
        [-x / 2, -y / 2, z], [x / 2, -y / 2, z], [x / 2, y / 2, z], [-x / 2, y / 2, z],
    ]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return _surface_geometry(vertices, None, faces)


def rhombicuboctahedron(x: float = 1.0, y: float = 1.0, z: float = 1.0) -> GeometryPrimitive:
    """Create a rhombicuboctahedron with dimensions ``x``, ``y``, and ``z``."""
    _validate_dimensions(x, y, z)
    value = 1 + np.sqrt(2)
    vertices_set = set()
    for coordinates in set(permutations((value, 1, 1))):
        for signs in product((-1, 1), repeat=3):
            vertices_set.add(tuple(sign * coordinate for sign, coordinate in zip(signs, coordinates)))
    vertices = sorted(vertices_set)
    faces = _convex_faces(np.asarray(vertices, dtype=float))
    geometry = _surface_geometry([list(vertex) for vertex in vertices], 'base_center', faces)
    normalize_geometry(geometry, 'base_center')
    geometry.transform(_scale_matrix([x, y, z]), center=[0.0, 0.0, 0.0])
    return geometry


def _validate_dimensions(x: float, y: float, z: float) -> None:
    """Validate that shape dimensions are strictly positive."""
    if x <= 0 or y <= 0 or z <= 0:
        raise ValueError('Shape dimensions must be positive')


def _scale_matrix(factor: list[float]):
    """Create a scale matrix for shape dimensions."""
    from pycityjson.model import TransformationMatrix

    return TransformationMatrix().scale(factor)


def _surface_geometry(vertices, local_origin, faces=None) -> GeometryPrimitive:
    """Build a surface geometry from vertices and indexed polygon faces."""
    if faces is None:
        faces = [(0, 1, 2, 3)]
    surfaces = [
        MultiLineString([MultiPoint([Point(*vertices[index]) for index in face])])
        for face in faces
    ]
    geometry = GeometryPrimitive(MultiSurface(surfaces), lod='1')
    return normalize_geometry(geometry, local_origin) if local_origin else geometry


def _convex_faces(vertices: np.ndarray) -> list[tuple[int, ...]]:
    """Find polygonal faces of a convex point set using coplanar triples."""
    face_sets: set[frozenset[int]] = set()
    center = vertices.mean(axis=0)
    for i, j, k in permutations(range(len(vertices)), 3):
        normal = np.cross(vertices[j] - vertices[i], vertices[k] - vertices[i])
        length = np.linalg.norm(normal)
        if length == 0:
            continue
        distances = (vertices - vertices[i]) @ normal
        if np.all(distances <= 1e-8) or np.all(distances >= -1e-8):
            indices = tuple(np.flatnonzero(np.abs(distances) < 1e-8))
            if len(indices) >= 3:
                ordered = _order_face(vertices, indices, normal, center)
                face_sets.add(frozenset(ordered))
    return sorted(_order_face(vertices, tuple(face), np.cross(
        vertices[next(iter(face))] - vertices[tuple(face)[1]],
        vertices[tuple(face)[2]] - vertices[tuple(face)[1]],
    ), vertices.mean(axis=0)) for face in face_sets)


def _order_face(vertices, indices, normal, center) -> tuple[int, ...]:
    """Order coplanar face vertices around their face center."""
    points = vertices[list(indices)]
    face_center = points.mean(axis=0)
    basis = points[0] - face_center
    basis /= np.linalg.norm(basis)
    second = np.cross(normal, basis)
    angles = np.arctan2((points - face_center) @ second, (points - face_center) @ basis)
    return tuple(indices[index] for index in np.argsort(angles))
