"""Elevation queries for modeled CityJSON surfaces."""

import numpy as np

from pycityjson.model import CityObject, GeometryPrimitive


def elevation_at_coordinate(
    ground_surface_object: CityObject,
    coordinate: tuple[float, float],
    relative: bool = True,
    lod: str = 'highest',
    n: int = 3,
) -> float:
    """Return the average height of the nearest terrain vertices.

    The search starts with a one-unit radius in X and Y and doubles until
    ``n`` vertices are found. ``coordinate`` is relative to the project
    origin by default; absolute coordinates are supported with
    ``relative=False``.
    """
    if n < 1:
        raise ValueError('n must be greater than zero')
    x, y = _relative_coordinate(ground_surface_object, coordinate, relative)
    geometries = _select_geometries(ground_surface_object, lod)
    vertices = np.asarray([
        vertex
        for geometry in geometries
        for vertex in geometry.get_vertices(flatten=True)
    ], dtype=float)
    if not len(vertices):
        raise ValueError(f'No surface contains coordinate ({coordinate[0]}, {coordinate[1]})')

    distances = np.sum((vertices[:, :2] - [x, y]) ** 2, axis=1)
    radius = 1.0
    maximum_radius = float(np.sqrt(np.max(distances)))
    while radius < maximum_radius:
        nearby = np.flatnonzero(distances <= radius**2)
        if len(nearby) >= n:
            break
        radius *= 2.0
    else:
        nearby = np.arange(len(vertices))

    selected = nearby[np.argsort(distances[nearby])[:n]]
    return float(np.mean(vertices[selected, 2]))


def _relative_coordinate(
    ground_surface_object: CityObject,
    coordinate: tuple[float, float],
    relative: bool,
) -> tuple[float, float]:
    """Convert an absolute coordinate to project-relative coordinates."""
    if relative:
        return coordinate
    project = getattr(ground_surface_object, 'project', None)
    if project is None:
        raise ValueError('Absolute coordinates require an object attached to a project')
    return coordinate[0] - project.project_origin[0], coordinate[1] - project.project_origin[1]


def _select_geometries(
    ground_surface_object: CityObject,
    lod: str,
) -> list[GeometryPrimitive]:
    """Select primitive geometries for the requested LoD."""
    geometries = [
        geometry
        for geometry in ground_surface_object.geometries
        if isinstance(geometry, GeometryPrimitive) and geometry.lod != 'origin'
    ]
    if lod != 'highest':
        return [geometry for geometry in geometries if geometry.lod == str(lod)]
    numeric = [geometry for geometry in geometries if _numeric_lod(geometry.lod) is not None]
    if not numeric:
        return geometries
    return [max(numeric, key=lambda geometry: _numeric_lod(geometry.lod))]


def _numeric_lod(lod: str) -> float | None:
    """Convert a numeric LoD to a float, returning None for named LoDs."""
    try:
        return float(lod)
    except ValueError:
        return None
