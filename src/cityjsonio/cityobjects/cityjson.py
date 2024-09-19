from src.cityjson import City, CityObjects, CityObject
from src.cityjson.cityobjects import CityGroup


class CityObjectsToCityJsonSerializer:
    def __init__(self, cityobjects: CityObjects, city: City):
        self.cityobjects = cityobjects
        self.city = city

    def _serialize_cityobject(self, cityobject: CityObject) -> dict:
        cj = {'type': cityobject.type}
        if cityobject.geo_extent is not None:
            cj['geographicalExtent'] = cityobject.geo_extent
        if cityobject.attributes != {}:
            cj['attributes'] = cityobject.attributes
        if len(cityobject.geometries) > 0:
            # todo rm city
            cj['geometry'] = [g.to_cj(self.city) for g in cityobject.geometries]
        if cityobject.children != []:
            cj['children'] = [child.uuid() for child in cityobject.children]
        if cityobject.parents != []:
            cj['parent'] = [parent.uuid() for parent in cityobject.parents]
        return cj

    def _serialize_citygroup(self, citygroup: CityGroup) -> dict:
        cj = self._serialize_cityobject(citygroup)
        if citygroup.children_roles != [] and len(citygroup.children_roles) == len(citygroup.children):
            cj['childrenRoles'] = citygroup.children_roles
        return cj

    def _serialize_one(self, cityobject: CityObject) -> dict:
        if cityobject.type == 'CityObjectGroup':
            return self._serialize_citygroup(cityobject)
        return self._serialize_cityobject(cityobject)

    def serialize(self) -> dict:
        city_objects = {}
        for cityobject in self.cityobjects:
            city_objects[cityobject.uuid()] = self._serialize_one(cityobject)
        return city_objects

