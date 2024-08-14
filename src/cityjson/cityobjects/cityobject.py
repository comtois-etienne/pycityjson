from src.guid import guid, is_guid
from src.scripts.attribute import round_attribute as _round
from src.cityjson.geometry import CityGeometry


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


class CityObject:
    def __init__(self, city, type, attributes=None, geometry=None, children=None, parent=None):
        self.city = city

        self.attributes = {} if attributes is None else attributes
        self.geometry: list[CityGeometry] = [] if geometry is None else geometry # todo verify that it is a list of geometries
        self.children = [] if children is None else children

        self.__uuid = self.attributes['uuid'] if 'uuid' in self.attributes else guid()
        self.type = type #todo verif with types
        self.geo_extent = None

        for child in self.children:
            child.set_parent(self)
        self.parent = parent

    def __repr__(self):
        return f"CityObject({self.type}({self.__uuid}))"

    def to_cj(self):
        cj = {'type': self.type}
        if self.geo_extent is not None:
            cj['geographicalExtent'] = self.geo_extent
        if self.attributes != {}:
            cj['attributes'] = self.attributes
        if self.geometry is not None:
            cj['geometry'] = [g.to_cj(self.city.get_vertices()) for g in self.geometry]
        if self.children != []:
            cj['children'] = [child.uuid() for child in self.children]
        if self.parent is not None:
            cj['parent'] = self.parent.uuid()
        return cj

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        self.children.append(child)
        child.set_parent(self)
        self.city.add_cityobject(child)

    def set_attribute(self, key, value):
        self.attributes[key] = value
        if key == 'uuid':
            self.__uuid = value

    def uuid(self):
        return self.__uuid

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
    
    def add_geometry(self, geometry):
        self.geometry.append(geometry)

    def get_vertices(self, flat=False):
        return [g.to_cj(self.city) for g in self.geometry]

    def set_geographical_extent(self, overwrite=False):
        if self.geo_extent is None or overwrite:
            g = self.get_geometry()[0] #todo multiple geometries
            self.geo_extent = [
                g.get_min(0), g.get_min(1), g.get_min(2),
                g.get_max(0), g.get_max(1), g.get_max(2)
            ]
        return self.geo_extent

    def is_uuid_valid(self):
        return is_guid(self.__uuid)

    def correct_uuid(self):
        if not is_guid(self.__uuid):
            self.set_attribute('uuid', guid())
        return self.__uuid


class CityGroup(CityObject):
    def __init__(self, city, attributes=None, geometry=None, children=None, parent=None, children_roles=None):
        super().__init__(
            city, 
            'CityObjectGroup', 
            attributes, 
            geometry, 
            children, 
            parent
        )
        self.children_roles = [] if children_roles is None else children_roles

    def add_child(self, child, role=None):
        super().add_child(child)
        if role is not None:
            self.children_roles.append(role)

    def to_cj(self):
        cj = super().to_cj()
        if self.children_roles != [] and len(self.children_roles) == len(self.children):
            cj['childrenRoles'] = self.children_roles
        return cj

