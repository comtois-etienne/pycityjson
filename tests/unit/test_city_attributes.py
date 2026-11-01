from pycityjson.model import City, CityObject, GeometryPrimitive, MultiPoint, Point


def _city_with_objects() -> tuple[City, CityObject, CityObject]:
    """Create a city with two objects for attribute API tests."""
    city = City()
    first = CityObject(city.cityobjects, 'Building', uuid='first')
    second = CityObject(city.cityobjects, 'Building', uuid='second')
    geometry = GeometryPrimitive(MultiPoint([Point(0, 0, 0)]), '1')
    first.add_geometry(geometry)
    second.add_geometry(geometry.duplicate())
    city.cityobjects.add_cityobject(first)
    city.cityobjects.add_cityobject(second)
    return city, first, second


def test_uuid_attribute_is_added_and_updated_at_all_levels():
    city, first, _ = _city_with_objects()

    original_uuid = first.uuid()
    first.add_uuid_as_attribute()
    assert first.uuid() == original_uuid
    assert first.attributes['uuid'] == original_uuid

    first.set_uuid('updated')
    assert first.uuid() == 'updated'
    assert first.attributes['uuid'] == 'updated'

    city.add_uuid_as_attribute()
    assert all(
        city_object.attributes['uuid'] == city_object.uuid()
        for city_object in city.cityobjects
    )

    city.set_uuid('shared')
    assert all(city_object.uuid() == 'shared' for city_object in city.cityobjects)
    assert all(
        city_object.attributes['uuid'] == 'shared'
        for city_object in city.cityobjects
    )

    city.remove_uuid_as_attribute()
    assert all(
        'uuid' not in city_object.attributes
        and city_object.uuid() == 'shared'
        for city_object in city.cityobjects
    )


def test_attributes_can_be_added_modified_and_filtered():
    city, first, second = _city_with_objects()

    city.set_attribute('status', 'new')
    assert first.get_attribute('status') == 'new'
    first.set_attribute('status', 'changed')
    assert first.get_attribute('status') == 'changed'

    city.cityobjects.set_attribute('status', 'shared')
    assert city.get_objects_by_attribute('status', 'shared') == [first, second]
    assert city.cityobjects.get_by_attribute('status', 'shared') == [first, second]


def test_lod_can_be_set_at_city_object_collection_and_city_levels():
    city, first, _ = _city_with_objects()

    first.set_lod(2)
    assert first.geometries[0].get_lod() == '2'
    city.cityobjects.set_lod('3')
    assert all(geometry.get_lod() == '3' for object_ in city.cityobjects for geometry in object_.geometries)
    city.set_lod(4)
    assert all(geometry.get_lod() == '4' for object_ in city.cityobjects for geometry in object_.geometries)
