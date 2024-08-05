from .citygeometry.citygeometry import CityGeometry
from src.uuid.guid import guid, is_guid
from src.scripts.attribute import get_attribute
from src.scripts.attribute import round_attribute as _round

FIRST_LEVEL_TYPES = [
    "Bridge",
    "Building",
    "CityFurniture",
    "CityObjectGroup",
    "GenericCityObject",
    "LandUse",
    "OtherConstruction",
    "PlantCover",
    "SolitaryVegetationObject",
    "TINRelief",
    "TransportSquare",
    "Railway",
    "Road",
    "Tunnel",
    "WaterBody",
    "WaterWay"
    # +Extension
]

# They need a first level parent to exist
SECOND_LEVEL_TYPES = {
    "Bridge": [
        "BridgePart",
        "BridgeInstallation",
        "BrigeConstructiveElement",
        "BridgeRoom",
        "BridgeFurniture",
    ],
    "Building": [
        "BuildingPart",
        "BuildingInstallation",
        "BuildingConstructiveElement",
        "BuildingFurniture",
        "BuildingStorey",
        "BuildingRoom",
        "BuildingUnit",
    ],
    "Tunnel": [
        "TunnelPart",
        "TunnelInstallation",
        "TunnelConstructiveElement",
        "TunnelHollowSpace",
        "TunnelFurniture",
    ],
}


def parse_cityobject(cityjson, uuid, data):
    ctobj = CityObject(
        cityjson = cityjson,
        type = get_attribute(data, 'type', 'GenericCityObject'),
        attributes = get_attribute(data, 'attributes', {}),
        geometry = CityGeometry(get_attribute(data, 'geometry', None), cityjson), #todo
        children = get_attribute(data, 'children', []), # todo link uuids to objects
        parent = get_attribute(data, 'parent', None) # todo link uuid to object
    )
    ctobj.geo_extent = get_attribute(data, 'geographicalExtent', None)
    ctobj.set_attribute('uuid', uuid)
    return ctobj


class CityObject:
    def __init__(self, cityjson, type, attributes={}, geometry=None, children=[], parent=None):
        self.cityjson = cityjson
        self._uuid = attributes['uuid'] if 'uuid' in attributes else guid()
        self.type = type #todo verif with types
        self.geo_extent = None
        self.attributes = attributes
        self.geometry = geometry
        self.children = children
        for child in self.children:
            child.set_parent(self)
        self.parent = parent

    def __repr__(self):
        return f"CityObject({self.type}({self._uuid}))"

    def to_cj(self):
        cj = {'type': self.type}
        if self.geo_extent is not None:
            cj['geographicalExtent'] = self.geo_extent
        if self.attributes != {}:
            cj['attributes'] = self.attributes
        if self.geometry is not None:
            cj['geometry'] = self.geometry.to_cj()
        if self.children != []:
            cj['children'] = [child.uuid for child in self.children]
        if self.parent is not None:
            cj['parent'] = self.parent.uuid
        return cj

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        self.children.append(child)
        child.set_parent(self)
        self.cityjson.add_cityobject(child)

    def set_attribute(self, key, value):
        self.attributes[key] = value
        if key == 'uuid':
            self._uuid = value

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

    def set_geographical_extent(self, overwrite=False):
        if self.geo_extent is None or overwrite:
            g = self.get_geometry()
            self.geo_extent = [
                g.get_min(0), g.get_min(1), g.get_min(2),
                g.get_max(0), g.get_max(1), g.get_max(2)
            ]
        return self.geo_extent

    def is_uuid_valid(self):
        print(self._uuid)
        return is_guid(self._uuid)

    def correct_uuid(self):
        if not is_guid(self._uuid):
            self.set_attribute('uuid', guid())
        return self._uuid



