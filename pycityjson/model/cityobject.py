import numpy as np

from pycityjson.guid import guid, is_guid

from .geometry import CityGeometry
from .matrix import TransformationMatrix
from .vertices import Vertex

FIRST_LEVEL_TYPES = [
    'Bridge',
    'Building',
    'CityFurniture',
    'CityObjectGroup',
    'GenericCityObject',
    'LandUse',
    'OtherConstruction',
    'PlantCover',
    'SolitaryVegetationObject',
    'TINRelief',
    'TransportSquare',
    'Railway',
    'Road',
    'Tunnel',
    'WaterBody',
    'WaterWay',
    # +Extension # todo implement
]

# They need a first level parent to exist
SECOND_LEVEL_TYPES = {
    'Bridge': [
        'BridgePart',
        'BridgeInstallation',
        'BrigeConstructiveElement',
        'BridgeRoom',
        'BridgeFurniture',
    ],
    'Building': [
        'BuildingPart',
        'BuildingInstallation',
        'BuildingConstructiveElement',
        'BuildingFurniture',
        'BuildingStorey',
        'BuildingRoom',
        'BuildingUnit',
    ],
    'Tunnel': [
        'TunnelPart',
        'TunnelInstallation',
        'TunnelConstructiveElement',
        'TunnelHollowSpace',
        'TunnelFurniture',
    ],
}


class CityObject:
    def __init__(
        self,
        cityobjects: 'CityObjects',
        type: str,
        attributes: dict = None,
        geometries: list[CityGeometry] = None,
        children=None,
        parents=None,
    ):
        self.cityobjects: 'CityObjects' = cityobjects

        self.attributes = {} if attributes is None else attributes
        self.geometries: list[CityGeometry] = [] if geometries is None else geometries  # todo verify that it is a list of geometries

        self.children: list[CityObject] | list[str] = [] if children is None else children
        self.parents: list[CityObject] | list[str] = [] if parents is None else parents

        self.__uuid: str = self.attributes['uuid'] if 'uuid' in self.attributes else guid()
        self.type: str = type  # todo verify with types
        self.geo_extent: Vertex = None  # [minx, miny, minz, maxx, maxy, maxz]

    def __repr__(self) -> str:
        return f'CityObject({self.type}({self.__uuid}))'

    def __str__(self) -> str:
        return f'{self.__uuid}'

    def __iter__(self):
        return iter(self.geometries)

    def add_parent(self, parent: 'CityObject') -> None:
        """
        :param parent: one of the parents of the CityObject
        """
        if parent not in self.parents:
            self.parents.append(parent)
            parent.add_child(self)
        self.cityobjects.add_cityobject(parent)

    def add_child(self, child: 'CityObject'):
        """
        :param child: one of the children of the CityObject
        """
        if child not in self.children:
            self.children.append(child)
            child.add_parent(self)
        self.cityobjects.add_cityobject(child)

    def get_attribute(self, key: str):
        """
        CityObject attributes are stored in a dictionary.
        They can contain any information about the object.
        :param key: the key of the attribute
        :return: the value of the attribute or None if it does not exist
        """
        return self.attributes[str(key)] if str(key) in self.attributes else None

    def set_attribute(self, key: str, value) -> None:
        """
        The value of the attribute is stored in a dictionary.
        If the key already exists, the value is overwritten.
        The key 'uuid' is reserved for the uuid of the CityObject and can be changed.
        :param key: the key of the attribute
        :param value: the value of the attribute
        """
        self.attributes[str(key)] = value
        if key == 'uuid':
            self.__uuid = value

    def uuid(self) -> str:
        """
        :return: the uuid of the CityObject as a string.
        """
        return self.__uuid

    def round_attribute(self, attribute: str, decimals=0) -> None:
        """
        May throw an error if the attribute is not a number
        :param attribute: the key of the attribute
        :param decimals: the number of decimals to round the attribute to. If 0, the attribute is rounded and converted to an integer
        """
        if attribute in self.attributes:
            self.set_attribute(attribute, round(self.get_attribute(attribute), decimals))
        if decimals == 0:
            self.set_attribute(attribute, int(self.get_attribute(attribute)))

    def rename_attribute(self, old_key: str, new_key: str) -> None:
        """
        Changes the key of an attribute.
        If the old key does not exist, nothing happens.
        Does not change the value of the attribute.
        :param old_key: the current key of the attribute
        :param new_key: the new key of the attribute
        """
        if old_key in self.attributes:
            self.attributes[new_key] = self.attributes.pop(old_key)

    def duplicate_attribute(self, old_key: str, new_key: str) -> None:
        """
        Duplicates an attribute.
        If the old key does not exist, nothing happens.
        :param old_key: the current key of the attribute
        :param new_key: the new key of the new attribute
        """
        if old_key in self.attributes:
            self.attributes[new_key] = self.attributes[old_key]

    def add_geometry(self, geometry: CityGeometry) -> None:
        """
        Adds a geometry to the CityObject.
        It should have a different LOD than the existing geometries.
        :param geometry: the geometry to add
        """
        self.geometries.append(geometry)

    def get_geometry(self, *, lod: str = '1') -> CityGeometry | None:
        """
        :param lod: the level of detail of the geometry
        :return: the geometry with the specified LOD or None if it does not exist
        """
        for geometry in self.geometries:
            if geometry.lod == lod:
                return geometry
        return None

    def get_vertices(self, flatten=False) -> list:
        """
        Returns the vertices of all the geometries of the CityObject.
        :param flatten: if True, the vertices are returned as a single list of vertices. If False, the vertices are returned as the boundaries of the geometries.
        """
        vertices = []
        for g in self.geometries:
            if flatten:
                vertices += g.get_vertices(flatten)
            else:
                vertices.append(g.get_vertices(flatten))
        return vertices

    def set_geographical_extent(self, overwrite=True) -> Vertex | None:
        """
        Sets the minimum and maximum coordinates of the CityObject.
        If the CityObject has no geometries, the extent is set to None.
        :param overwrite: if True, the extent is recalculated even if it already exists. If False, the extent is only calculated if it does not exist.
        """
        if overwrite is False and self.geo_extent is not None:
            return self.geo_extent
        if len(self.geometries) == 0:
            return None

        vertices = np.array(self.get_vertices(flatten=True))
        o_min = np.min(vertices, axis=0)
        o_max = np.max(vertices, axis=0)
        self.geo_extent = [o_min[0], o_min[1], o_min[2], o_max[0], o_max[1], o_max[2]]
        return self.geo_extent

    def is_uuid_valid(self):
        """
        This is only to check if it is a unique identifier.
        This is not a CityJSON requirement. Just good practice.
        :return: True if the uuid is a valid IFC GUID or UUID, False otherwise.
        """
        return is_guid(self.__uuid)

    def correct_uuid(self):
        """
        Sets the uuid to a new GUID if it is not a valid GUID.
        This is not a CityJSON requirement. Just good practice.
        :return: the new uuid of the CityObject
        """
        if not is_guid(self.__uuid):
            self.set_attribute('uuid', guid())
        return self.__uuid

    def is_cityobjectgroup(self) -> bool:
        """
        :return: True if the CityObject type is a CityObjectGroup, False otherwise.
        """
        return self.type == 'CityObjectGroup'

    def to_cityobjectgroup(self, children_roles=None) -> 'CityObjectGroup':
        """
        Converts the CityObject to a CityObjectGroup.
        It has an additional attribute to store the roles of the children. It is not mandatory in CityJSON.
        :param children_roles: the roles of the children of the CityObjectGroup
        :return: the CityObjectGroup
        """
        return CityObjectGroup(
            self.cityobjects,
            self.attributes,
            self.geometries,
            self.children,
            self.parents,
            children_roles,
        )

    def transform(self, matrix: TransformationMatrix, center: Vertex = None) -> None:
        """
        The center by default is the center of the geographical extent at ground level.
        The center of an instance geometry is used if it exists so the transformations are consistent.
        :param matrix: the transformation matrix to apply to all the geometries
        :param center: the center from which the transformation is applied
        """
        if center is None:
            # default center if no center is given
            geo_extent = self.set_geographical_extent()
            center = [
                (geo_extent[0] + geo_extent[3]) / 2,
                (geo_extent[1] + geo_extent[4]) / 2,
                geo_extent[2],
            ]
            # find the center of an instance geometry for consistency
            for geometry in self.geometries:
                if geometry.is_geometry_instance():
                    center = geometry.get_origin()
                    break

        for geometry in self.geometries:
            geometry.transform(matrix, center)
        _ = self.set_geographical_extent()

    def to_geometry_primitive(self) -> None:
        """
        Converts all the geometries of the CityObject to GeometryPrimitive so no GeometryInstance are used.
        """
        for i, geometry in enumerate(self.geometries):
            self.geometries[i] = geometry.to_geometry_primitive()


class CityObjectGroup(CityObject):
    """
    This class extends CityObject to represent a CityObjectGroup.
    It can also contain geometries and attributes.
    It has an additional attribute that can be used to store the roles of the children.
    """

    def __init__(
        self,
        cityobjects: 'CityObjects',
        attributes: dict = None,
        geometries: list[CityGeometry] = None,
        children: list[CityObject] = None,
        parent: list[CityObject] = None,
        children_roles: list[str] = None,
    ):
        """
        :param cityobjects: the parent class containing all the CityObjects
        :param attributes: the attributes of the CityObjectGroup
        :param geometries: the geometries of the CityObjectGroup
        :param children: the children of the CityObjectGroup
        """
        super().__init__(cityobjects, 'CityObjectGroup', attributes, geometries, children, parent)
        self.children_roles = [] if children_roles is None else children_roles

    def add_child(self, child: CityObject, role: str = None) -> None:
        """
        Adds a child to the CityObjectGroup with a role.
        :param child: the child to add
        :param role: the role of the child. Not mandatory in CityJSON.
        """
        len_before = len(self.children)
        super().add_child(child)
        if len(self.children) > len_before and role is not None:
            self.children_roles.append(role)


class CityObjects:
    def __init__(self, cityobjects: list[CityObject] = None):
        self.__cityobjects: list[CityObject] = [] if cityobjects is None else cityobjects

    def __len__(self) -> int:
        """
        returns the number of CityObject
        """
        return len(self.__cityobjects)

    def __repr__(self):
        return f'{self.__cityobjects}'

    def __getitem__(self, key: int | str) -> CityObject | None:
        """
        Returns a CityObject by index or by uuid
        :param key: the index or the uuid of the CityObject
        :return: the CityObject or None if it does not exist
        """
        if isinstance(key, int):
            if key < len(self.__cityobjects) and key >= 0:
                return self.__cityobjects[key]
            return None
        return self.get_by_uuid(key)

    def __iter__(self):
        """
        Iterates over the CityObjects
        """
        return iter(self.__cityobjects)

    def get_by_type(self, citytype: str) -> list[CityObject]:
        """
        :param citytype: the type of the CityObject
        :return: a list of CityObject of the specified type. Empty list if none are found.
        """
        city_objects = []
        for cityobject in self.__cityobjects:
            if cityobject['type'] == citytype:
                city_objects.append(cityobject)
        return city_objects

    def round_attribute(self, attribute: str, decimals=0):
        """
        Rounds an attribute of all the CityObjects if it exists.
        :param attribute: the key of the attribute
        :param decimals: the number of decimals to round the attribute to. If 0, the attribute is rounded and converted to an integer
        """
        for cityobject in self.__cityobjects:
            if attribute in cityobject.attributes:
                cityobject.round_attribute(attribute, decimals)

    def get_by_uuid(self, uuid: str) -> CityObject | None:
        """
        :param uuid: the uuid of the CityObject
        :return: the CityObject with the specified uuid or None if it does not exist
        """
        for city_object in self.__cityobjects:
            if city_object.uuid() == uuid:
                return city_object
        return None

    def add_cityobject(self, cityobject: CityObject) -> None:
        """
        Adds a CityObject to the collection if it does not already exist.
        :param cityobject: the CityObject to add
        """
        city_object = self.get_by_uuid(cityobject.uuid())
        if city_object is None:
            self.__cityobjects.append(cityobject)

    def get_by_attribute(self, attribute: str, value) -> list[CityObject]:
        """
        :param attribute: the key of the attribute
        :param value: the value of the attribute
        :return: a list of CityObject with the attribute which has the specified value. Empty list if none are found.
        """
        city_objects = []
        for city_object in self.__cityobjects:
            if attribute in city_object.attributes and city_object.attributes[attribute] == value:
                city_objects.append(city_object)
        return city_objects

    def tolist(self) -> list[CityObject]:
        """
        :return: a list of all the CityObjects
        """
        return [cityobject for cityobject in self.__cityobjects]
