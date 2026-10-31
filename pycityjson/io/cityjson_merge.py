import json
from copy import deepcopy
from pathlib import Path

from pycityjson.model import (
    City,
    CityGeometry,
    CityObject,
    GeometryPrimitive,
    MultiLineString,
    MultiPoint,
    MultiSolid,
    MultiSurface,
    Point,
    Primitive,
    Solid,
)

from .cityjson_input import CityParser


def _cityjson_paths(directory: Path) -> list[Path]:
    """Return CityJSON files from a directory in a stable order."""
    return sorted(path for path in directory.iterdir() if path.name.endswith('.city.json'))


def _copy_city_settings(source: City, target: City) -> None:
    """Copy root-level settings from the first source city."""
    target.type = source.type
    target.version = source.version
    target.metadata = deepcopy(source.metadata)
    target.extensions = deepcopy(source.extensions)
    target.extra_root_properties = deepcopy(source.extra_root_properties)
    target.scale = source.scale.copy()
    target.origin = source.origin.copy()
    target.default_theme_texture = source.default_theme_texture
    target.default_theme_material = source.default_theme_material
    target.textures = deepcopy(source.textures)
    target.texture_vertices = deepcopy(source.texture_vertices)


def _copy_appearance(source: City, target: City) -> None:
    """Add materials from a source city to the merged city."""
    for material in source.materials:
        target.materials.add(material)


def _as_surface(primitive: Primitive) -> MultiSurface:
    """Promote a primitive to a MultiSurface."""
    if isinstance(primitive, MultiSurface):
        return primitive
    if isinstance(primitive, MultiLineString):
        return MultiSurface([primitive])
    if isinstance(primitive, MultiPoint):
        return MultiSurface([MultiLineString([primitive])])
    raise TypeError(f'Cannot promote {primitive.get_type()} to MultiSurface')


def _as_solid(primitive: Primitive) -> Solid:
    """Promote a primitive to a Solid."""
    if isinstance(primitive, Solid):
        return primitive
    return Solid([_as_surface(primitive)])


def _merge_primitives(primitives: list[Primitive]) -> Primitive:
    """Merge primitives and promote them to a common CityJSON type."""
    if not primitives:
        raise ValueError('At least one primitive is required')
    if all(isinstance(primitive, MultiSurface) for primitive in primitives):
        surfaces = [
            surface
            for primitive in primitives
            for surface in primitive.children
        ]
        return MultiSurface(surfaces)
    if all(isinstance(primitive, MultiSolid) for primitive in primitives):
        solids = [
            solid
            for primitive in primitives
            for solid in primitive.children
        ]
        return MultiSolid(solids)
    if len(primitives) == 1:
        return primitives[0]
    return MultiSolid([
        _as_solid(primitive)
        for primitive in primitives
    ])


def _merge_geometries(geometries: list[CityGeometry]) -> list[GeometryPrimitive]:
    """Merge geometries by LoD while preserving their geometry semantics."""
    grouped: dict[str, list[GeometryPrimitive]] = {}
    for geometry in geometries:
        primitive_geometry = geometry.to_geometry_primitive()
        grouped.setdefault(primitive_geometry.get_lod(), []).append(primitive_geometry)
    return [
        GeometryPrimitive(
            _merge_primitives([geometry.primitive for geometry in grouped[lod]]),
            lod,
        )
        for lod in grouped
    ]


def _unique_uuid(city: City, preferred: str, index: int) -> str:
    """Return a CityObject identifier that is unique in the merged city."""
    candidate = preferred
    suffix = 1
    while city.cityobjects.get_by_uuid(candidate) is not None:
        candidate = f'{preferred}_{index}_{suffix}'
        suffix += 1
    return candidate


def _add_separate_objects(cities: list[City], merged: City) -> None:
    """Copy all source objects into the merged city separately."""
    object_index = 0
    for city in cities:
        for source_object in city.cityobjects:
            uuid = _unique_uuid(merged, source_object.uuid(), object_index)
            object_index += 1
            city_object = CityObject(
                merged.cityobjects,
                source_object.type,
                attributes=deepcopy(source_object.attributes),
                geometries=_merge_geometries(source_object.geometries),
                uuid=uuid,
            )
            merged.cityobjects.add_cityobject(city_object)


def _add_merged_objects(cities: list[City], merged: City) -> None:
    """Merge source objects with the same CityObject type."""
    grouped: dict[str, list[CityObject]] = {}
    for city in cities:
        for city_object in city.cityobjects:
            grouped.setdefault(city_object.type, []).append(city_object)
    for index, (object_type, objects) in enumerate(grouped.items()):
        geometries = [
            geometry
            for city_object in objects
            for geometry in city_object.geometries
        ]
        city_object = CityObject(
            merged.cityobjects,
            object_type,
            geometries=_merge_geometries(geometries),
            uuid=_unique_uuid(merged, object_type, index),
        )
        merged.cityobjects.add_cityobject(city_object)


def _average_xy_vertices(city: City) -> None:
    """Average Z values for points sharing the same X and Y coordinates."""
    points: list[Point] = []
    for city_object in city.cityobjects:
        for geometry in city_object.geometries:
            primitive = geometry.to_geometry_primitive().primitive
            points.extend(_points_in_primitive(primitive))
    heights: dict[tuple[float, float], list[float]] = {}
    for point in points:
        heights.setdefault((point.x, point.y), []).append(point.z)
    for point in points:
        point.z = sum(heights[(point.x, point.y)]) / len(heights[(point.x, point.y)])


def _points_in_primitive(primitive: Primitive) -> list[Point]:
    """Return all Point instances contained by a primitive."""
    if isinstance(primitive, Point):
        return [primitive]
    points: list[Point] = []
    for child in primitive.children:
        points.extend(_points_in_primitive(child))
    return points


def merge_cityjson_directory(
    directory: str | Path,
    *,
    merge_objets: bool = False,
    average_adjacent_vertices: bool = False,
) -> City:
    """
    Merge CityJSON files from a directory into one CityJSON model.
    :param directory: directory containing `.city.json` files.
    :param directory: directory containing `.city.json` files.
    :param merge_objets: merge objects with the same CityObject type.
    :param average_adjacent_vertices: average Z values for points sharing X and Y.
    :return: merged CityJSON model.
    """
    source_paths = _cityjson_paths(Path(directory))
    if not source_paths:
        raise ValueError(f'No .city.json files found in {directory}')
    cities = [
        CityParser(json.loads(path.read_text())).parse()
        for path in source_paths
    ]
    merged = City()
    _copy_city_settings(cities[0], merged)
    for city in cities:
        _copy_appearance(city, merged)
    if merge_objets:
        _add_merged_objects(cities, merged)
    else:
        _add_separate_objects(cities, merged)
    if average_adjacent_vertices:
        _average_xy_vertices(merged)
    merged.set_geographical_extent()
    return merged
