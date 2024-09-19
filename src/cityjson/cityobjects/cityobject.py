from src.guid import guid, is_guid
from src.cityjson.geometry import CityGeometry
import numpy as np


def _round_attribute(data, attribute, decimals=0):
    if attribute in data:
        data[attribute] = round(data[attribute], decimals)
    if decimals == 0:
        data[attribute] = int(data[attribute])


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
    # +Extension # todo implement
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
    def __init__(self, cityobjects, type, attributes=None, geometries=None, children=None, parents=None):
        self.cityobjects = cityobjects

        self.attributes = {} if attributes is None else attributes
        self.geometries: list[CityGeometry] = [] if geometries is None else geometries # todo verify that it is a list of geometries
        
        self.children = [] if children is None else children
        self.parents = [] if parents is None else parents

        self.__uuid = self.attributes['uuid'] if 'uuid' in self.attributes else guid()
        self.type = type #todo verif with types
        self.geo_extent = None

    def __repr__(self):
        return f"CityObject({self.type}({self.__uuid}))"

    def add_parent(self, parent):
        if parent not in self.parents:
            self.parents.append(parent)
            parent.add_child(self)
        self.cityobjects.add_cityobject(parent)

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)
            child.add_parent(self)
        self.cityobjects.add_cityobject(child)

    def get_attribute(self, key):
        return self.attributes[key] if key in self.attributes else None

    def set_attribute(self, key, value):
        self.attributes[key] = value
        if key == 'uuid':
            self.__uuid = value

    def uuid(self):
        return self.__uuid

    def round_attribute(self, attribute, decimals=0):
        _round_attribute(self.attributes, attribute, decimals)

    def rename_attribute(self, old_key, new_key):
        if old_key in self.attributes:
            self.attributes[new_key] = self.attributes.pop(old_key)

    def duplicate_attribute(self, old_key, new_key):
        if old_key in self.attributes:
            self.attributes[new_key] = self.attributes[old_key]
    
    def add_geometry(self, geometry: CityGeometry):
        self.geometries.append(geometry)

    def get_vertices(self, flatten=False):
        vertices = []
        for g in self.geometries:
            if flatten:
                vertices += g.get_vertices(flatten)
            else:
                vertices.append(g.get_vertices(flatten))
        return vertices

    # todo test
    def set_geographical_extent(self, overwrite=True):
        if overwrite is False and self.geo_extent is not None:
            return self.geo_extent
        if len(self.geometries) == 0:
            return None

        o_min, o_max = self.geometries[0].get_min_max()
        o_min, o_max = np.array(o_min), np.array(o_max)
        for geometry in self.geometries[1:]:
            g_min, g_max = geometry.get_min_max()
            o_min = np.minimum(o_min, np.array(g_min))
            o_max = np.maximum(o_max, np.array(g_max))

        self.geo_extent = [o_min[0], o_min[1], o_min[2], o_max[0], o_max[1], o_max[2]]
        return self.geo_extent

    def is_uuid_valid(self):
        return is_guid(self.__uuid)

    def correct_uuid(self):
        if not is_guid(self.__uuid):
            self.set_attribute('uuid', guid())
        return self.__uuid

    def is_citygroup(self):
        return self.type == 'CityObjectGroup'

    def to_citygroup(self, children_roles=None) -> 'CityGroup':
        return CityGroup(
            self.cityobjects,
            self.attributes,
            self.geometries,
            self.children,
            self.parents,
            children_roles
        )

    # center by default is the center of the geographical extent at ground level
    # use the center of an instance geometry if it exists so the transformations are consistent
    def transform(self, matrix, center=None):
        if center is None:
            geo_extent = self.set_geographical_extent()
            center = [
                (geo_extent[0] + geo_extent[3]) / 2, 
                (geo_extent[1] + geo_extent[4]) / 2, 
                geo_extent[2]
            ]
        for geometry in self.geometries:
            geometry.transform(matrix, center)
        self.set_geographical_extent()

    def to_geometry_primitive(self):
        for i, geometry in enumerate(self.geometries):
            self.geometries[i] = geometry.to_geometry_primitive()


class CityGroup(CityObject):
    def __init__(self, cityobjects, attributes=None, geometries=None, children=None, parent=None, children_roles=None):
        super().__init__(
            cityobjects, 
            'CityObjectGroup', 
            attributes, 
            geometries, 
            children, 
            parent
        )
        self.children_roles = [] if children_roles is None else children_roles

    def add_child(self, child, role=None):
        super().add_child(child)
        if role is not None:
            self.children_roles.append(role)

