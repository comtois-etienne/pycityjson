from .primitive.primitive import Primitive
from .matrix import TransformationMatrix

class CityGeometry:
    def transform(self, matrix):
        pass

    def get_lod(self) -> str:
        pass

    def get_vertices(self, flatten):
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
        return f'Geometry{self.primitive.get_type()}(lod={self.lod})'

    def __repr__(self) -> str:
        return f'Geometry((lod({self.lod}))({repr(self.primitive)}))'

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Geometry):
            return False
        return self.__repr__() == repr(value)

    def get_lod(self) -> str:
        return self.lod

    def get_vertices(self, flatten=False):
        return self.primitive.get_vertices(flatten)

    def to_cj(self, city) -> dict:
        vertices = city.get_vertices()
        citygeometry = {
            'type': self.primitive.get_type(),
            'lod': self.lod,
            'boundaries': self.primitive.to_cj(vertices)
        }
        semantics = self.primitive.get_semantic_surfaces()
        if semantics is not None:
            citygeometry['semantics'] = {
                'surfaces': semantics,
                'values': self.primitive.get_semantic_values(semantics)
            }
        return citygeometry


# Contains 'GeometryInstance' (Template)
class GeometryInstance(CityGeometry):
    def __init__(self, geometry: Geometry, matrix: TransformationMatrix):
        self.geometry = geometry
        self.origin = [0, 0, 0]
        self.matrix = matrix

    def get_vertices(self, flatten=False):
        vertices = self.geometry.get_vertices(flatten)
        matrix = self.matrix.move(self.origin)
        return matrix.reproject_vertices(vertices)

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
            'transformationMatrix': self.matrix.to_cj()
        }
        return cityinstance

