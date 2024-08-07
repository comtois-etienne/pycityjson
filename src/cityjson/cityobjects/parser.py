from src.scripts.attribute import get_attribute
from .cityobject import CityObject
from .cityobjects import CityObjects
from src.cityjson.geometry import CityGeometryParser


class CityObjectParser:
    def __init__(self, city):
        self.city = city
        self.geometry_parser = CityGeometryParser(self.city)

    def _link_children(self, city_object, city_objects):
        children = []
        for child_uuid in city_object.children:
            child = city_objects.get_by_uuid(child_uuid)
            children.append(child) if child is not None else None
        city_object.children = children

    def _link_parent(self, city_object, city_objects):
        if city_object.parent is not None:
            city_object.parent = city_objects.get_by_uuid(city_object.parent)
    
    # data contains cityjson['CityObjects'][uuid]
    def parse(self, uuid, data):
        geometry = [self.geometry_parser.parse(g) for g in get_attribute(data, 'geometry', default=[])]
        # todo citygroupparser
        city_object = CityObject(
            city = self.city,
            type = get_attribute(data, 'type', default='GenericCityObject'),
            attributes = get_attribute(data, 'attributes', default={}),
            geometry = geometry,
            children = get_attribute(data, 'children', default=[]), # todo link uuids to objects
            parent = get_attribute(data, 'parent', default=None) # todo link uuid to object
        )
        city_object.geo_extent = get_attribute(data, 'geographicalExtent', default=None)
        city_object.set_attribute('uuid', uuid)
        return city_object


class CityObjectsParser:
    def __init__(self, city):
        self.city = city

    # data contains cityjson['CityObjects']
    def parse(self, data) -> CityObjects:
        city_objects = []
        parser = CityObjectParser(self.city)
        for uuid, data in data.items():
            city_objects.append(parser.parse(uuid, data))
        # todo sort the data?

        city_objects = CityObjects(self.city, city_objects)
        for city_object in city_objects:
            parser._link_parent(city_object, city_objects)
            parser._link_children(city_object, city_objects)

        return city_objects

