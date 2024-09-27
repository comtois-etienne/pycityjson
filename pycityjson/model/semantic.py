from pycityjson.guid import guid

SEMANTIC = {
    # for "Building", "BuildingPart", "BuildingRoom", "BuildingStorey", "BuildingUnit", "BuildingInstallation"
    'roof': 'RoofSurface',
    'ground': 'GroundSurface',
    'wall': 'WallSurface',
    'closure': 'ClosureSurface',
    'outer_ceiling': 'OuterCeilingSurface',
    'outer_floor': 'OuterFloorSurface',
    'window': 'Window',
    'door': 'Door',
    'interior_wall': 'InteriorWallSurface',
    'ceiling': 'CeilingSurface',
    'floor': 'FloorSurface',
    # for "WaterBody"
    'water': 'WaterSurface',
    'water_ground': 'WaterGroundSurface',
    'water_closure': 'WaterClosureSurface',
    # for "Road", "Railway", "TransportSquare"
    'road': 'TrafficArea',
    'auxiliary_road': 'AuxiliaryTrafficArea',
    'marking': 'TransportationMarking',
    'hole': 'TransportationHole',
}


class Semantic:
    """
    Contains the semantic of a MultiLineString (Surface)
    Can also be used to strore more metadata about the surface.
    """

    def __init__(self, dtype: str, add_uuid: bool = True):
        """
        :param dtype: name of the CityJSON semantic - will be converted to the standard semantic if possible.
        :param add_uuid: bool, if True, an IFC UUID is added to the semantic to the 'uuid' key.
        """
        self.__semantic = {}
        self.__semantic['type'] = self.__get_semantic(dtype)
        if add_uuid:
            self.add_uuid()

    def __getitem__(self, key: str) -> str:
        """
        :param key: key of the semantic dictionary.
        :return: value of the key.
        """
        return self.__semantic[key]

    def __setitem__(self, key: str, value: str) -> None:
        """
        :param key: key of the semantic dictionary.
        :param value: value to set.
        """
        self.__semantic[key] = value

    def __repr__(self):
        return f'Semantic({self.__semantic})'

    def __eq__(self, other: object) -> bool:
        """
        :param other: object to compare.
        :return: True if the semantics are the same and have the same UUID if it exists.
        """
        if isinstance(other, Semantic) or isinstance(other, dict):
            if other['type'] == self.__semantic['type']:
                if 'uuid' in other and 'uuid' in self.__semantic:
                    return other['uuid'] == self.__semantic['uuid']
                if 'uuid' in other or 'uuid' in self.__semantic:
                    return False
                return True
        return False

    def add_uuid(self, uuid: str = None) -> None:
        """
        Adds a UUID to the semantic
        :param uuid: IFC UUID if no uuid is provided. a new one is generated.
        """
        self.__semantic['uuid'] = guid() if uuid is None else uuid

    def to_dict(self) -> dict:
        """
        :return: a copy of the semantic dictionary.
        """
        return self.__semantic.copy()

    @staticmethod
    def __get_semantic(name: str) -> str | None:
        """
        Work in progress
        Returns the semantic by the CityJSON name or by a simplified name.
        Add a '+' in front of the name if it is not a simplified name. Used for the extended semantic.
        :param name: name of the CityJSON semantic.
        :return: the standard semantic name.
        """
        if name is None:
            return None
        if name in SEMANTIC:
            return SEMANTIC[name]
        if name in SEMANTIC.values():
            return name
        name = name.replace(' ', '')
        # todo : to be implemented
        if not name.startswith('+'):
            name = '+' + name
        return name
