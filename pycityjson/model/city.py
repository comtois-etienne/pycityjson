from .cityobject import CityObjects
from .template import GeometryTemplates
from .vertices import Vertices


class City:
    def __init__(self, type='CityJSON', version='2.0'):
        self.type = type
        self.version = version
        self.metadata = {}
        self.scale = [0.001, 0.001, 0.001]
        self.origin = [0, 0, 0]
        precision = self.precision()
        self.vertices = Vertices(precision=precision) # Must be initialized after the scale
        self.geometry_templates = GeometryTemplates([], Vertices(precision=precision))
        self.cityobjects = CityObjects()

    def __getitem__(self, key):
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

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def precision(self) -> int:
        return len(str(self.scale[0]).split('.')[1])

    def set_origin(self, vertice=None):
        if vertice is None:
            x = self.vertices.get_min(0)
            y = self.vertices.get_min(1)
            z = self.vertices.get_min(2)
            vertice = [x, y, z]
        self.origin = vertice

    def epsg(self):
        if 'referenceSystem' not in self.metadata:
            return None
        epsg_path = self.metadata['referenceSystem']
        return int(epsg_path.split('/')[-1])

    def set_epsg(self, epsg=2950):
        self.metadata['referenceSystem'] = f'https://www.opengis.net/def/crs/EPSG/0/{epsg}'

    def set_geographical_extent(self):
        self.metadata['geographicalExtent'] = [
            self.vertices.get_min(0),
            self.vertices.get_min(1),
            self.vertices.get_min(2),
            self.vertices.get_max(0),
            self.vertices.get_max(1),
            self.vertices.get_max(2),
        ]
