from src.scripts.attribute import get_attribute
from src.cityjson import City, CityObject, CityObjects
from ..geometry import CityGeometryParser


class CityObjectParser:
    def __init__(self, city: City):
        self.city = city
        self.geometry_parser = CityGeometryParser(self.city)

    def _link_children(self, city_object, city_objects):
        children_uuids = city_object.children
        city_object.children = []
        for child_uuid in children_uuids:
            child = city_objects.get_by_uuid(child_uuid)
            city_object.add_child(child) if child is not None else None

    def _link_parents(self, city_object, city_objects):
        parents_uuids = city_object.parents
        city_object.parents = []
        for parent_uuid in parents_uuids:
            parent = city_objects.get_by_uuid(parent_uuid)
            city_object.add_parent(parent) if parent is not None else None
    
    # data contains cityjson['CityObjects'][uuid]
    def parse(self, uuid, data) -> CityObject:
        geometry = [self.geometry_parser.parse(g) for g in get_attribute(data, 'geometry', default=[])]

        city_object = CityObject(
            cityobjects = self.city.cityobjects,
            type = get_attribute(data, 'type', default='GenericCityObject'),
            attributes = get_attribute(data, 'attributes', default={}),
            geometries = geometry,
            children = get_attribute(data, 'children', default=[]),
            parents = get_attribute(data, 'parents', default=None)
        )

        city_object.geo_extent = get_attribute(data, 'geographicalExtent', default=None)
        city_object.set_attribute('uuid', uuid)
        if city_object.type == 'CityObjectGroup':
            city_object = city_object.to_citygroup(get_attribute(data, 'children_roles', default=[]))
        return city_object


class CityObjectsParser:
    def __init__(self, city):
        self.city = city

    # data contains cityjson['CityObjects']
    def parse(self, data) -> CityObjects:
        city_objects = CityObjects()
        parser = CityObjectParser(self.city)

        for uuid, data in data.items():
            cityobject = parser.parse(uuid, data)
            city_objects.add_cityobject(cityobject)

        for city_object in city_objects:
            parser._link_parents(city_object, city_objects)
            parser._link_children(city_object, city_objects)

        return city_objects

