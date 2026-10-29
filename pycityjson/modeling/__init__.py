"""Convenience tools for creating and transforming CityJSON models."""

from .elevation import elevation_at_coordinate
from .geometry import normalize_geometry
from .project import CityObjectType, ModelingObject, ModelingProject
from .shapes import cuboid, rectangle, rhombicuboctahedron

__all__ = [
    'CityObjectType',
    'ModelingObject',
    'ModelingProject',
    'cuboid',
    'elevation_at_coordinate',
    'normalize_geometry',
    'rectangle',
    'rhombicuboctahedron',
]