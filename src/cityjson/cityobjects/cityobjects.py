from .cityobject import CityObject


class CityObjects:
    def __init__(self, cityobjects = None):
        self._cityobjects : list[CityObject] = [] if cityobjects is None else cityobjects

    def __len__(self):
        return len(self._cityobjects)

    def __repr__(self):
        return f'{self._cityobjects}'

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._cityobjects[key]
        return self.get_by_uuid(key)

    def __iter__(self):
        return iter(self._cityobjects)

    def _get_by_type(self, citytype):
        city_objects = []
        for cityobject in self._cityobjects:
            if cityobject['type'] == citytype:
                city_objects.append(cityobject)
        return city_objects

    def round_attribute(self, attribute, decimals=0):
        for cityobject in self._cityobjects:
            cityobject.round_attribute(attribute, decimals)

    def get_by_uuid(self, uuid) -> CityObject:
        for city_object in self._cityobjects:
            if city_object.uuid() == uuid:
                return city_object
        return None

    def add_cityobject(self, cityobject: CityObject):
        ctobj = self.get_by_uuid(cityobject.uuid())
        if ctobj is None:
            self._cityobjects.append(cityobject)

    def get_by_attribute(self, attribute, value):
        city_objects = []
        for city_object in self._cityobjects:
            if attribute in city_object.attributes and city_object.attributes[attribute] == value:
                city_objects.append(city_object)
        return city_objects

