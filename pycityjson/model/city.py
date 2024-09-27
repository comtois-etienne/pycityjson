from .cityobject import CityObjects
from .template import GeometryTemplates
from .vertices import Vertex, Vertices


class City:
    def __init__(self, type: str = 'CityJSON', version: str = '2.0'):
        self.type: str = type
        self.version: str = version
        self.metadata: dict = {}
        self.scale: Vertex = [0.001, 0.001, 0.001]
        self.origin: Vertex = [0, 0, 0]
        precision = self.precision()
        self.vertices: Vertices = Vertices(precision=precision)  # Must be initialized after the scale
        self.geometry_templates: GeometryTemplates = GeometryTemplates([], Vertices(precision=precision))
        self.cityobjects: CityObjects = CityObjects()

    def __getitem__(self, key: str | int):
        """
        Used to access the city model as if it was a CityJSON
        :param key: int are used to access the vertices, str are used to access the city attributes
        """
        if isinstance(key, int):
            return self.vertices[key]

        key_lower = str(key).lower()
        if key_lower == 'vertices':
            return self.vertices
        if key_lower == 'cityobjects' or key_lower == 'objects':
            return self.cityobjects
        if key_lower == 'geometrytemplate' or key_lower == 'geometry-template':
            return self.geometry_templates
        if key_lower == 'epsg':
            return self.epsg()
        if key_lower == 'version':
            return self.version
        if key_lower == 'metadata':
            return self.metadata
        if key_lower == 'type':
            return self.type
        if key_lower == 'transform':
            return self.scale, self.origin
        if key_lower == 'scale':
            return self.scale
        if key_lower == 'origin':
            return self.origin
        return self.cityobjects[key]

    def __setitem__(self, key: str, value: str | int | list):
        """
        add metadata to the city model
        :param key: the key of the metadata
        :param value: the value of the metadata
        """
        self.metadata[key] = value

    def precision(self) -> int:
        """
        returns the number of decimal places to save the vertices
        3 decimal places is the default value and gives a precision of 1 mm
        2 decimal places gives a precision of 1 cm
        """
        return len(str(self.scale[0]).split('.')[1])

    def set_origin(self, vertex=None):
        """
        Set the origin (base point) of the city model
        Will not change the coordinates of the vertices or move the city objects
        :param vertex: The coordinates of the origin
        """
        if vertex is None:
            vertex = self.vertices.get_min()
        self.origin = vertex

    def epsg(self) -> int | None:
        """
        return the EPSG code of the city model
        """
        if 'referenceSystem' not in self.metadata:
            return None
        epsg_path = self.metadata['referenceSystem']
        return int(epsg_path.split('/')[-1])

    def set_epsg(self, epsg=2950) -> None:
        """
        Set the projection standard of the city model
        :param epsg: The EPSG code of the projection standard
        """
        self.metadata['referenceSystem'] = f'https://www.opengis.net/def/crs/EPSG/0/{epsg}'

    def set_geographical_extent(self) -> None:
        """
        Set minimum and maximum coordinates of the city model
        Will only use the vertices of the city objects that were loaded from a file
        Save and reopen the file to update the geographical extent with new city objects
        """
        min_x, min_y, min_z = self.vertices.get_min()
        max_x, max_y, max_z = self.vertices.get_max()
        self.metadata['geographicalExtent'] = [
            min_x,
            min_y,
            min_z,
            max_x,
            max_y,
            max_z,
        ]
