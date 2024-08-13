from .cityobjects import CityObjects
from .vertices.vertices import Vertices
from .template import GeometryTemplate


class City:
    def __init__(self, type='CityJSON', version='2.0'):
        self.type = type
        self.version = version
        self.metadata = {}
        self.scale = [0.001, 0.001, 0.001]
        self.origin = [0, 0, 0]
        self._vertices = None
        self._cityobjects = None
        self.geometry_template = None

    def get_vertices(self):
        if self._vertices is None:
            self._vertices = Vertices(self)
        return self._vertices
    
    def get_cityobjects(self):
        if self._cityobjects is None:
            self._cityobjects = CityObjects(self)
        return self._cityobjects
    
    def get_geometry_template(self):
        if self.geometry_template is None:
            self.geometry_template = GeometryTemplate(self)
        return self.geometry_template

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.get_vertices()[key]
        
        key_lower = str(key).lower()
        if key_lower == 'vertices':
            return self.get_vertices()
        if key_lower == 'cityobjects' or key_lower == 'objects':
            return self.get_cityobjects()
        if key_lower == 'geometrytemplate' or key_lower == 'geometry-template':
            return self.get_geometry_template()
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
        return self.get_cityobjects()[key]
    
    def __setitem__(self, key, value):
        self.metadata[key] = value
    
    def to_cj(self, purge_vertices=False):
        if purge_vertices:
            self._vertices = Vertices(self)
        city = {
            'type': self.type,
            'version': self.version,
            'CityObjects': self._cityobjects.to_cj(),
            'transform': {
                'scale': self.scale,
                'translate': self.origin
            },
            'vertices': self._vertices.to_cj(),
            'metadata': self.metadata,
        }
        if not self.geometry_template.is_empty():
            city['geometry-templates'] = self.geometry_template.to_cj()
        return city
    
    def precision(self):
        return len(str(self.scale[0]).split('.')[1])
    
    def set_origin(self, vertice=None):
        if vertice is None:
            x = self._vertices.get_min(0)
            y = self._vertices.get_min(1)
            z = self._vertices.get_min(2)
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
            self._vertices.get_min(0), self._vertices.get_min(1), self._vertices.get_min(2),
            self._vertices.get_max(0), self._vertices.get_max(1), self._vertices.get_max(2)
        ]

