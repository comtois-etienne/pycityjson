from .primitive.primitive import Primitive
from .matrix import TransformationMatrix


import numpy as np


class CityGeometry:
    def transform(self, matrix: TransformationMatrix):
        pass

    def get_lod(self) -> str:
        pass

    def get_vertices(self, flatten):
        pass

    # todo test
    def get_min_max(self):
        vertices = self.get_vertices(flatten=True)
        vertices = np.array(vertices)
        min_x = np.min(vertices, axis=0)[0]
        min_y = np.min(vertices, axis=0)[1]
        min_z = np.min(vertices, axis=0)[2]
        max_x = np.max(vertices, axis=0)[0]
        max_y = np.max(vertices, axis=0)[1]
        max_z = np.max(vertices, axis=0)[2]
        return [min_x, min_y, min_z], [max_x, max_y, max_z]

    def duplicate(self) -> 'CityGeometry':
        pass

    def to_geometry_primitive(self) -> 'GeometryPrimitive':
        pass

    def to_geometry_instance(self) -> 'GeometryInstance':
        # todo
        pass

    def to_cj(self, city) -> dict:
        pass


# Contains MultiSolid, Solid, MultiSurface, MultiLineString...
class GeometryPrimitive(CityGeometry):
    def __init__(self, primitive: Primitive, lod: str = '1'):
        self.primitive = primitive
        self.lod = lod

    def __str__(self) -> str:
        return f'Geometry{self.primitive.get_type()}(lod={self.lod})'

    def __repr__(self) -> str:
        return f'Geometry((lod({self.lod}))({repr(self.primitive)}))'

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, GeometryPrimitive):
            return False
        return self.__repr__() == repr(value)

    def transform(self, matrix: TransformationMatrix):
        self.primitive.transform(matrix)

    def get_lod(self) -> str:
        return self.lod

    def get_vertices(self, flatten=False):
        return self.primitive.get_vertices(flatten)

    def duplicate(self) -> CityGeometry:
        return GeometryPrimitive(self.primitive.copy(), self.lod)

    def to_geometry_primitive(self) -> 'GeometryPrimitive':
        return self

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
    def __init__(self, geometry: GeometryPrimitive, matrix: TransformationMatrix):
        self.geometry = geometry
        self.matrix = matrix

    def transform(self, matrix: TransformationMatrix):
        self.matrix = self.matrix.dot(matrix)

    def get_lod(self) -> str:
        return self.geometry.get_lod()

    def get_vertices(self, flatten=False):
        vertices = self.geometry.get_vertices(flatten)
        return self.matrix.reproject_vertices(vertices)

    def duplicate(self) -> CityGeometry:
        return GeometryInstance(self.geometry, self.matrix.copy())

    def to_geometry_primitive(self) -> GeometryPrimitive:
        primitive = self.geometry.primitive.copy()
        primitive.transform(self.matrix)
        return GeometryPrimitive(primitive, self.geometry.lod)

    def to_cj(self, city) -> dict:
        vertices = city.get_vertices()
        boundary = vertices.add(self.matrix.get_origin())

        geometry_templates = city.get_geometry_templates()
        template_index = geometry_templates.add_template(self.geometry)

        cityinstance = {
            'type': 'GeometryInstance',
            'template': template_index,
            'boundaries': [boundary],
            'transformationMatrix': self.matrix.recenter().to_cj()
        }
        return cityinstance

