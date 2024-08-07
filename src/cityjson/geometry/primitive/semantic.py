from src.uuid import guid


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


def _get_semantic(name):
    if name is None:
        return None
    if name in SEMANTIC:
        return SEMANTIC[name]
    if name in SEMANTIC.values():
        return name
    name = name.replace(" ", "")
    if not name.startswith('+'):
        name = '+' + name
    return name


class Semantic:
    def __init__(self, dtype: str):
        self.semantic = {}
        self.semantic['type'] = _get_semantic(dtype)
        self.add_uuid()

    def __getitem__(self, key):
        return self.semantic[key]
    
    def __setitem__(self, key, value):
        self.semantic[key] = value

    def __eq__(self, other):
        if isinstance(other, Semantic):
            if other['type'] == self.semantic['type']:
                if 'uuid' in other.semantic and 'uuid' in self.semantic:
                    return other['uuid'] == self.semantic['uuid']
                if 'uuid' in other.semantic or 'uuid' in self.semantic:
                    return False
                return True
        return False

    def add_uuid(self, uuid: str = None):
        self.semantic['uuid'] = guid() if uuid is None else uuid

    def to_cj(self):
        return self.semantic


class SemanticParser:
    def __init__(self, city):
        self.city = city

    def parse(self, data) -> list[Semantic]:
        semantics = []
        for s in data:
            semantic = Semantic(s['type'])
            for key, value in s.items():
                semantic[key] = value
            semantics.append(semantic)
        return semantics

