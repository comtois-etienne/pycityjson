from .cityobject import CityObject
import numpy as np


def parse_cityobjects(cityjson):
    pass


class CityObjects:
    # def __init__(self, cityjson):
    #     self._cityobjects = []
    #     city_objects = cityjson._data['CityObjects'] if 'CityObjects' in cityjson._data else {}
    #     for uuid, data in city_objects.items():
    #         self._cityobjects.append(CityObject(uuid, data, cityjson))

    def __init__(self, cityjson, cityobjects = []):
        self._cityjson = cityjson
        self._cityobjects = cityobjects

    def __len__(self):
        return len(self._cityobjects)

    def __repr__(self):
        return f'{self._cityobjects}'

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._cityobjects[key]
        return self.get_by_uuid(key)

    def _get_by_type(self, citytype):
        city_objects = []
        for cityobject in self._cityobjects:
            if cityobject['type'] == citytype:
                city_objects.append(cityobject)
        return city_objects
    
    def round_attribute(self, attribute, decimals=0):
        for cityobject in self._cityobjects:
            cityobject.round_attribute(attribute, decimals)
    
    def get_by_uuid(self, uuid):
        for city_object in self._cityobjects:
            if city_object.uuid == uuid:
                return city_object
        return None
    
    def add_cityobject(self, cityobject):
        ctobj = self.get_by_uuid(cityobject.uuid)
        if ctobj is None:
            self._cityobjects.append(cityobject)

    def get_by_attribute(self, attribute, value):
        city_objects = []
        for city_object in self._cityobjects:
            if attribute in city_object.attributes and city_object.attributes[attribute] == value:
                city_objects.append(city_object)
        return city_objects

    def to_cj(self):
        city_objects = {}
        for cityobject in self._cityobjects:
            city_objects[cityobject.uuid] = cityobject.to_cj()
        return city_objects

