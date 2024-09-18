from src.cityjson import City, Vertices


class CityToCityJsonSerializer:
    def __init__(self, city: City):
        self.city = city

    def serialize(self, purge_vertices=True) -> dict:
        self.city.get_vertices()
        self.city.get_cityobjects()
        self.city.get_geometry_templates()

        if purge_vertices:
            self.city._vertices = Vertices(self.city)

        city_dict = {
            'type': self.city.type,
            'version': self.city.version,
            'CityObjects': self.city._cityobjects.to_cj(),
            'transform': {
                'scale': self.city.scale,
                'translate': self.city.origin
            },
            'vertices': self.city._vertices.to_cj()
        }
        if not self.city._geometry_template.is_empty():
            city_dict['geometry-templates'] = self.city._geometry_template.to_cj()
        city_dict['metadata'] = self.city.metadata

        return city_dict

