from .geometry import GeometryPrimitive
from .vertices import Vertices


class GeometryTemplates:
    """
    Contains a list of GeometryPrimitive that can be used for GeometryInstance.
    It also contains the vertices that are used by the GeometryPrimitive.
    The vertices are shared between all the templates and separate from the city model vertices.
    """

    def __init__(self, geometries: list[GeometryPrimitive], vertices: Vertices):
        self.geometries = geometries
        self.vertices = vertices

    def __getitem__(self, key: int) -> GeometryPrimitive | None:
        """
        :param key: index of the GeometryPrimitive
        :return: GeometryPrimitive at the given index. None if the index is out
        """
        if key < 0 or key >= len(self.geometries):
            return None
        if isinstance(key, int):
            return self.geometries[key]
        return None

    def is_empty(self) -> bool:
        """
        :return: True if the list of geometries is empty, False otherwise
        """
        return len(self.geometries) == 0

    def add_template(self, city_geometry: GeometryPrimitive) -> int:
        """
        Adds a GeometryPrimitive to the list of geometries
        Will not add the same GeometryPrimitive multiple times (based on the __eq__ method)
        :param city_geometry: GeometryPrimitive to add
        :return: Index of the added GeometryPrimitive
        """
        if city_geometry not in self.geometries:
            self.geometries.append(city_geometry)
        return self.geometries.index(city_geometry)
