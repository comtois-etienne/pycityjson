"""Geometry normalization helpers for procedural modeling."""

from collections.abc import Sequence

import numpy as np

from pycityjson.model import CityGeometry, GeometryPrimitive


def normalize_geometry(
    geometry: CityGeometry,
    local_origin: str = 'base_center',
) -> CityGeometry:
    """Scale a geometry to unit size and place its local origin at the origin.

    Three-dimensional geometries are scaled by their height (the Z extent).
    Flat geometries are scaled by their longest horizontal side. ``local_origin`` may
    be ``base_center``, ``min``, ``max``, or one of the four base corners
    ``bottom_left``, ``bottom_right``, ``top_left``, and ``top_right``.
    """
    vertices = np.asarray(geometry.get_vertices(flatten=True), dtype=float)
    if vertices.size == 0:
        raise ValueError('Cannot normalize a geometry without vertices')
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError('Geometry vertices must have three coordinates')

    minimum = vertices.min(axis=0)
    maximum = vertices.max(axis=0)
    extent = maximum - minimum
    if extent[2] > 0:
        scale = 1.0 / extent[2]
    else:
        horizontal_extent = extent[:2]
        longest_side = float(horizontal_extent.max())
        if longest_side <= 0:
            raise ValueError('Cannot normalize a degenerate geometry')
        scale = 1.0 / longest_side

    origin_point = _local_origin_point(vertices, minimum, maximum, local_origin)
    matrix = _transformation(scale, -origin_point * scale)
    geometry.transform(matrix, center=[0.0, 0.0, 0.0])
    return geometry


def _local_origin_point(
    vertices: np.ndarray,
    minimum: np.ndarray,
    maximum: np.ndarray,
    local_origin: str,
) -> np.ndarray:
    """Return a local-origin coordinate from a bounding box."""
    if local_origin == 'base_center':
        return np.array([(minimum[0] + maximum[0]) / 2, (minimum[1] + maximum[1]) / 2, minimum[2]])
    if local_origin in {'min', 'bottom_left'}:
        return minimum
    if local_origin == 'max':
        return maximum
    corners = {
        'bottom_left': [minimum[0], minimum[1], minimum[2]],
        'bottom_right': [maximum[0], minimum[1], minimum[2]],
        'top_left': [minimum[0], maximum[1], minimum[2]],
        'top_right': [maximum[0], maximum[1], minimum[2]],
    }
    if local_origin in corners:
        return np.asarray(corners[local_origin], dtype=float)
    if local_origin.endswith('_point'):
        corner_name = local_origin.removesuffix('_point')
        if corner_name in corners:
            target = np.asarray(corners[corner_name], dtype=float)
            candidates = vertices[np.isclose(vertices[:, 2], minimum[2])]
            if len(candidates):
                return candidates[np.argmin(np.linalg.norm(candidates - target, axis=1))]
    raise ValueError(f'Unknown geometry local origin: {local_origin}')


def _transformation(scale: float, translation: Sequence[float]):
    """Create a transformation matrix for uniform scaling and translation."""
    from pycityjson.model import TransformationMatrix

    return TransformationMatrix().scale([scale, scale, scale]).translate(list(translation))
