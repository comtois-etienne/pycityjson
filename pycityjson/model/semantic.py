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


class Semantics:
    @staticmethod
    def __clean_dict(d):
        return {k: v for k, v in vars(d).items() if not k.startswith('_')}

    @staticmethod
    def to_dict():
        return {
            'ObjectParent': Semantics.__clean_dict(Semantics.ObjectParent),
            'ObjectChild': {
                'Bridge': Semantics.__clean_dict(Semantics.ObjectChild.Bridge),
                'Building': Semantics.__clean_dict(Semantics.ObjectChild.Building),
                'Tunnel': Semantics.__clean_dict(Semantics.ObjectChild.Tunnel),
            },
            'Surfaces': {
                'Building': Semantics.__clean_dict(Semantics.Surfaces.Building),
                'BuildingPart': Semantics.__clean_dict(Semantics.Surfaces.Building),
                'BuildingRoom': Semantics.__clean_dict(Semantics.Surfaces.Building),
                'BuildingStorey': Semantics.__clean_dict(Semantics.Surfaces.Building),
                'BuildingUnit': Semantics.__clean_dict(Semantics.Surfaces.Building),
                'BuildingInstallation': Semantics.__clean_dict(Semantics.Surfaces.Building),
                'WaterBody': Semantics.__clean_dict(Semantics.Surfaces.WaterBody),
                'Road': Semantics.__clean_dict(Semantics.Surfaces.Road),
                'Railway': Semantics.__clean_dict(Semantics.Surfaces.Road),
                'TransportSquare': Semantics.__clean_dict(Semantics.Surfaces.Road),
            },
        }

    class ObjectParent:
        BRIDGE = 'Bridge'
        BUILDING = 'Building'
        CITY_FURNITURE = 'CityFurniture'
        CITY_OBJECT_GROUP = 'CityObjectGroup'
        GENERIC_CITY_OBJECT = 'GenericCityObject'
        LAND_USE = 'LandUse'
        OTHER_CONSTRUCTION = 'OtherConstruction'
        PLANT_COVER = 'PlantCover'
        SOLITARY_VEGETATION_OBJECT = 'SolitaryVegetationObject'
        TIN_RELIEF = 'TINRelief'
        TRANSPORT_SQUARE = 'TransportSquare'
        RAILWAY = 'Railway'
        ROAD = 'Road'
        TUNNEL = 'Tunnel'
        WATER_BODY = 'WaterBody'
        WATER_WAY = 'WaterWay'
        # +Extension # todo implement

    class ObjectChild:
        """
        They need a parent to be valid.
        """

        class Bridge:
            BRIDGE_PART = 'BridgePart'
            BRIDGE_INSTALLATION = 'BridgeInstallation'
            BRIGE_CONSTRUCTIVE_ELEMENT = 'BrigeConstructiveElement'
            BRIDGE_ROOM = 'BridgeRoom'
            BRIDGE_FURNITURE = 'BridgeFurniture'

        class Building:
            BUILDING_PART = 'BuildingPart'
            BUILDING_INSTALLATION = 'BuildingInstallation'
            BUILDING_CONSTRUCTIVE_ELEMENT = 'BuildingConstructiveElement'
            BUILDING_FURNITURE = 'BuildingFurniture'
            BUILDING_STOREY = 'BuildingStorey'
            BUILDING_ROOM = 'BuildingRoom'
            BUILDING_UNIT = 'BuildingUnit'

        class Tunnel:
            TUNNEL_PART = 'TunnelPart'
            TUNNEL_INSTALLATION = 'TunnelInstallation'
            TUNNEL_CONSTRUCTIVE_ELEMENT = 'TunnelConstructiveElement'
            TUNNEL_HOLLOW_SPACE = 'TunnelHollowSpace'
            TUNNEL_FURNITURE = 'TunnelFurniture'

    class Surfaces:
        """
        Used for MultiLineString
        """

        class Building:
            ROOF_SURFACE = 'RoofSurface'
            GROUND_SURFACE = 'GroundSurface'
            WALL_SURFACE = 'WallSurface'
            CLOSURE_SURFACE = 'ClosureSurface'
            OUTER_CEILING_SURFACE = 'OuterCeilingSurface'
            OUTER_FLOOR_SURFACE = 'OuterFloorSurface'
            WINDOW = 'Window'
            DOOR = 'Door'
            INTERIOR_WALL_SURFACE = 'InteriorWallSurface'
            CEILING_SURFACE = 'CeilingSurface'
            FLOOR_SURFACE = 'FloorSurface'

        class BuildingPart(Building):
            pass

        class BuildingRoom(Building):
            pass

        class BuildingStorey(Building):
            pass

        class BuildingUnit(Building):
            pass

        class BuildingInstallation(Building):
            pass

        class WaterBody:
            WATER_SURFACE = 'WaterSurface'
            WATER_GROUND_SURFACE = 'WaterGroundSurface'
            WATER_CLOSURE_SURFACE = 'WaterClosureSurface'

        class Road:
            TRAFFIC_AREA = 'TrafficArea'
            AUXILIARY_TRAFFIC_AREA = 'AuxiliaryTrafficArea'
            TRANSPORTATION_MARKING = 'TransportationMarking'
            TRANSPORTATION_HOLE = 'TransportationHole'

        class Railway(Road):
            pass

        class TransportSquare(Road):
            pass


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
