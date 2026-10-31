import json
from pathlib import Path
from typing import Any

from pycityjson.guid import guid
from pycityjson.model import (
    City,
    CityObject,
    GeometryPrimitive,
    MultiLineString,
    MultiPoint,
    MultiSurface,
    Point,
    Primitive,
)

from .coordinates import reproject_coordinates


def _point(coordinate: list[float]) -> Point:
    """Create a three-dimensional point from a GeoJSON position."""
    values = [*coordinate[:3], 0.0]
    return Point(values[0], values[1], values[2])


def _points(coordinates: list[list[float]]) -> MultiPoint:
    """Create a CityJSON ring from coordinate positions."""
    return MultiPoint([_point(coordinate) for coordinate in coordinates])


def _polygon(coordinates: list[list[list[float]]]) -> MultiSurface:
    """Create a CityJSON surface from polygon rings."""
    return MultiSurface([MultiLineString([_points(ring) for ring in coordinates])])


def _geometry_primitive(geometry: dict[str, Any]) -> Primitive:
    """Convert one GeoJSON geometry to a CityJSON primitive."""
    geometry_type = geometry['type']
    coordinates = geometry['coordinates']
    if geometry_type == 'Point':
        return _points([coordinates])
    if geometry_type == 'MultiPoint':
        return _points(coordinates)
    if geometry_type == 'LineString':
        return MultiLineString([_points(coordinates)])
    if geometry_type == 'MultiLineString':
        return MultiLineString([_points(line) for line in coordinates])
    if geometry_type == 'Polygon':
        return _polygon(coordinates)
    if geometry_type == 'MultiPolygon':
        return MultiSurface([
            surface
            for polygon in coordinates
            for surface in _polygon(polygon).children
        ])
    raise ValueError(f'Unsupported GeoJSON geometry type: {geometry_type}')


def _feature_geometry(
    feature: dict[str, Any],
    epsg: int,
    destination: int | None,
) -> GeometryPrimitive | None:
    """Convert and parse a GeoJSON feature geometry."""
    geometry = feature.get('geometry')
    if geometry is None:
        return None
    converted = dict(geometry)
    if destination is not None:
        converted['coordinates'] = reproject_coordinates(
            geometry['coordinates'],
            epsg,
            destination,
        )
    return GeometryPrimitive(_geometry_primitive(converted), '0')


def _feature_id(feature: dict[str, Any]) -> str:
    """Return a stable feature identifier, generating one when absent."""
    return str(feature.get('id', guid()))


def _load_feature(
    feature: dict[str, Any],
    city: City,
    epsg: int,
    destination: int | None,
) -> tuple[str, dict[str, Any]]:
    """Load one GeoJSON feature into the City model."""
    feature_id = _feature_id(feature)
    properties = feature.get('properties') or {}
    city_object = CityObject(
        city.cityobjects,
        'GenericCityObject',
        attributes=properties,
        uuid=feature_id,
    )
    geometry = _feature_geometry(feature, epsg, destination)
    if geometry is not None:
        city_object.add_geometry(geometry)
    city.cityobjects.add_cityobject(city_object)
    return feature_id, properties


def read_geojson(
    file_path: str | Path,
    epsg: int,
    convert_to_epsg: int | None = None,
) -> City:
    """
    Load a GeoJSON FeatureCollection into a City model.

    :param file_path: path to the GeoJSON file.
    :param epsg: EPSG code of the coordinates in the GeoJSON file.
    :param convert_to_epsg: optional EPSG code for output coordinates.
    :return: City model containing the GeoJSON features.
    """
    data = json.loads(Path(file_path).read_text())
    if data.get('type') != 'FeatureCollection':
        raise ValueError('GeoJSON input must be a FeatureCollection')
    city = City()
    city.metadata['geojson'] = {
        key: value
        for key, value in data.items()
        if key not in {'type', 'features'}
    }
    properties: dict[str, dict[str, Any]] = {}
    for feature in data.get('features', []):
        feature_id, feature_properties = _load_feature(
            feature,
            city,
            epsg,
            convert_to_epsg,
        )
        properties[feature_id] = feature_properties
    city.metadata['geojson']['properties'] = properties
    city.metadata['referenceSystem'] = (
        f'https://www.opengis.net/def/crs/EPSG/0/'
        f'{convert_to_epsg if convert_to_epsg is not None else epsg}'
    )
    city.set_geographical_extent()
    return city


load_geojson = read_geojson
