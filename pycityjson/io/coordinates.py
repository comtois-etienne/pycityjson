from collections.abc import Sequence

from pyproj import Transformer

Coordinate = list[float]


def reproject_coordinates(
    coordinates: Sequence,
    epsg_source: int,
    epsg_destination: int,
) -> list:
    """
    Reproject a nested GeoJSON coordinate structure between EPSG systems.

    :param coordinates: coordinate or nested coordinate sequences.
    :param epsg_source: EPSG code of the source coordinate reference system.
    :param epsg_destination: EPSG code of the destination coordinate reference system.
    :return: coordinates with the same nesting and converted coordinate values.
    """
    transformer = Transformer.from_crs(
        epsg_source,
        epsg_destination,
        always_xy=True,
    )
    return _reproject_coordinate_structure(coordinates, transformer)


def _reproject_coordinate_structure(coordinates: Sequence, transformer: Transformer) -> list:
    """Reproject one coordinate or recurse through nested coordinates."""
    if _is_coordinate(coordinates):
        x, y = transformer.transform(coordinates[0], coordinates[1])
        return [x, y, *coordinates[2:]]
    return [
        _reproject_coordinate_structure(value, transformer)
        for value in coordinates
    ]


def _is_coordinate(value: Sequence) -> bool:
    """Return whether a sequence is one coordinate position."""
    return len(value) >= 2 and all(isinstance(item, (int, float)) for item in value)
