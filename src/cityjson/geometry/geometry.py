from .primitive.primitive import Primitive
from src.scripts.matrix import identity_matrix


class CityGeometry:
    def transform(self, matrix):
        pass

    def get_lod(self) -> str:
        pass

    def get_boundaries(self):
        pass
    
    def get_vertices(self):
        pass

    def get_max(self, axis=0):
        pass

    def get_min(self, axis=0):
        pass

    def to_geometry(self) -> 'Geometry':
        pass

    def to_cj(self, city) -> dict:
        pass


# Contains MultiSolid, Solid, MultiSurface, MultiLineString...
class Geometry(CityGeometry):
    def __init__(self, primitive: Primitive, lod: str = '1'):
        self.primitive = primitive
        self.lod = lod

    def __str__(self) -> str:
        return f'{self.primitive.get_type()}(lod {self.lod})'

    def __repr__(self) -> str:
        return f'Geometry((lod({self.lod}))({repr(self.primitive)}))'

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Geometry):
            return False
        return self.__repr__() == repr(value)

    def get_lod(self) -> str:
        return self.lod

    def get_vertices(self):
        return self.primitive.get_vertices()

    def to_cj(self, city) -> dict:
        vertices = city.get_vertices()
        citygeometry = {
            'type': self.primitive.get_type(),
            'lod': self.lod,
            'boundaries': self.primitive.to_cj(vertices)
        }
        semantics = self.primitive.get_semantic_surfaces()
        if semantics is not None and semantics[0]['type'] is not None:
            citygeometry['semantics'] = {
                'surfaces': semantics,
                'values': self.primitive.get_semantic_values(semantics)
            }
        return citygeometry


# Contains 'GeometryInstance' (Template)
class GeometryInstance(CityGeometry):
    def __init__(self, geometry: Geometry):
        self.geometry = geometry
        self.origin = [0, 0, 0]
        self.matrix = identity_matrix()

    def transform(self, matrix):
        # todo
        pass

    def get_lod(self) -> str:
        return self.geometry.get_lod()

    def to_cj(self, city) -> dict:
        vertices = city.get_vertices()
        boundary = vertices.add(self.origin)

        geometry_templates = city.get_geometry_templates()
        template_index = geometry_templates.add_template(self.geometry)

        cityinstance = {
            'type': 'GeometryInstance',
            'template': template_index,
            'boundaries': [boundary],
            'transformationMatrix': self.matrix
        }
        return cityinstance

