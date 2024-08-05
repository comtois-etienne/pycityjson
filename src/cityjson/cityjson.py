import json
import numpy as np

from .cityobjects import CityObjects
from .cityvertices import CityVertices
from src.scripts.attribute import get_attribute, get_nested_attribute


class CityJSON:
    def __init__(self, file_path):
        self._file_path = file_path
        self._data = self._read_json()

        self._scale: list = get_attribute(self._data, 'scale', [0.001, 0.001, 0.001])
        self._translate: list = get_nested_attribute(self._data, 'transform', 'translate', [0, 0, 0])
        self.metadata: dict = get_attribute(self._data, 'metadata', {})
        self.vertices = CityVertices(self)
        self.cityobjects = CityObjects(self)

    def _read_json(self):
        with open(self._file_path, 'r') as file:
            return json.load(file)

    def _write_json(self):
        pass

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.get_vertices()[key]
        
        key_lower = str(key).lower()
        if key_lower == 'vertices':
            return self.get_vertices()
        if key_lower == 'cityobjects' or key_lower == 'objects':
            return self.get_cityobjects()
        if key_lower == 'buildings':
            return self.get_buildings()
        if key_lower == 'vegetations':
            return self.get_vegetations()
        if key_lower == 'epsg':
            return self.epsg()
        if key_lower == 'version':
            return self._data['version']
        if key_lower == 'metadata':
            return self.metadata
        if key_lower == 'type':
            return self._data['type']
        if key_lower == 'transform':
            return self.origin(), self.scale()
        return self.get_cityobjects()[key]
    
    def __setitem__(self, key, value):
        self.metadata[key] = value
    
    def to_cj(self):
        return {
            'type': self._data['type'],
            'version': self._data['version'],
            'CityObjects': self.cityobjects.to_cj(),
            'transform': {
                'scale': self.scale(),
                'translate': self.origin()
            },
            'vertices': self.vertices.to_cj(),
            'metadata': self.metadata,
        }
    
    def precision(self):
        return len(str(self._scale[0]).split('.')[1])
    
    def origin(self):
        return self._translate
    
    def set_origin(self, x=None, y=None, z=None):
        if x is None or y is None or z is None:
            x = self.vertices.get_min(0)
            y = self.vertices.get_min(1)
            z = self.vertices.get_min(2)
            print(x, y, z)
        self._translate = [x, y, z]
        self.vertices.set_origin(x, y, z)
    
    def scale(self):
        return self._scale

    def epsg(self):
        if 'referenceSystem' not in self.metadata:
            return None
        epsg_path = self.metadata['referenceSystem']
        return int(epsg_path.split('/')[-1])
    
    def set_epsg(self, epsg=2950):
        self.metadata['referenceSystem'] = f'https://www.opengis.net/def/crs/EPSG/0/{epsg}'
    
    def get_vertices(self):
        return self.vertices

    def get_cityobjects(self):
        return self.cityobjects

    def get_buildings(self):
        return self.cityobjects._get_by_type('Building')
    
    def get_vegetations(self):
        return self.cityobjects._get_by_type('SolitaryVegetationObject')
    
    def set_geographical_extent(self):
        self.metadata['geographicalExtent'] = [
            self.vertices.get_min(0), self.vertices.get_min(1), self.vertices.get_min(2),
            self.vertices.get_max(0), self.vertices.get_max(1), self.vertices.get_max(2)
        ]
    
    # def add_uuid_attribute(self):
    #     for key in self.get_cityobjects():
    #         self.get_cityobject(key).add_uuid()
    
    # def rename_attribute(self, old_key, new_key):
    #     for key in self.get_cityobjects():
    #         self.get_cityobject(key).rename_attribute(old_key, new_key)

    #todo
    # def correct_uuid(self):
    #     for key in self.get_cityobjects():
    #         pass