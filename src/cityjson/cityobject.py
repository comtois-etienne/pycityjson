from .citygeometry.citygeometry import CityGeometry
from src.uuid.guid import guid, is_guid
from src.scripts.attribute import get_attribute
from src.scripts.attribute import round_attribute as _round

# todo remove _data

class CityObject:
    def __init__(self, uuid, data, cityjson):
        self.cityjson = cityjson
        self.uuid = uuid
        self.type = get_attribute(data, 'type', 'Building')
        self.extent = get_attribute(data, 'geographicalExtent', [])
        self.attributes = get_attribute(data, 'attributes', {})
        self.geometry = CityGeometry(data['geometry'], cityjson)
        self.set_attribute('uuid', self.uuid)

    def __repr__(self):
        return f"CityObject({self.type}({self.uuid}))"

    def to_dict(self):
        return {
            'type': self.type,
            'geographicalExtent': self.extent,
            'attributes': self.attributes,
            'geometry': self.geometry.to_dict()
        }

    def set_attribute(self, key, value):
        self.attributes[key] = value

    def round_attribute(self, attribute, decimals=0):
        _round(self.attributes, attribute, decimals)

    def rename_attribute(self, old_key, new_key):
        if old_key in self.attributes:
            self.attributes[new_key] = self.attributes.pop(old_key)

    def duplicate_attribute(self, old_key, new_key):
        if old_key in self.attributes:
            self.attributes[new_key] = self.attributes[old_key]

    def get_geometry(self):
        return self.geometry

    def get_vertices(self, flat=False):
        return self.geometry.get_vertices(flat)

    def add_geographical_extent(self, overwrite=False):
        if 'geographicalExtent' not in self._data or overwrite:
            g = self.get_geometry()
            self._data['geographicalExtent'] = [
                g.get_min(0), g.get_min(1), g.get_min(2),
                g.get_max(0), g.get_max(1), g.get_max(2)
            ]
        return self._data['geographicalExtent']

    def is_uuid_valid(self):
        print(self.uuid)
        return is_guid(self.uuid)

    def correct_uuid(self):
        if not is_guid(self.uuid):
            self.uuid = guid()
            self.set_attribute('uuid', self.uuid)
        return self.uuid



