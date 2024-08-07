from .cityobject import CityObject


class Building(CityObject):
    def __init__(self, cityjson, attributes={}, geometry=[], children=[], parent=None):
        super().__init__(
            cityjson, 
            'Building', 
            attributes, 
            geometry, 
            children, 
            parent
        )

