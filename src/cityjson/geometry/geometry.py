from .primitive.primitive import Primitive
from .matrix import TransformationMatrix

import numpy as np


class CityGeometry:
    def transform(self, matrix: TransformationMatrix, center=None):
        pass

    def get_lod(self) -> str:
        pass

    def get_vertices(self, flatten):
        pass

    # todo test
    def get_min_max(self):
        vertices = self.get_vertices(flatten=True)
        vertices = np.array(vertices)
        v_min = np.min(vertices, axis=0)
        v_max = np.max(vertices, axis=0)
        return v_min.tolist(), v_max.tolist()

    # different than copy - see each implementation
    def duplicate(self) -> 'CityGeometry':
        pass

    def get_origin(self):
        pass

    def to_geometry_primitive(self) -> 'GeometryPrimitive':
        pass

    def to_geometry_instance(self) -> 'GeometryInstance':
        # todo
        pass

    def as_geometry_primitive(self) -> 'GeometryPrimitive':
        return self

    def as_geometry_instance(self) -> 'GeometryInstance':
        return self

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

    # GeometryPrimitive doens't have a transformation matrix
    # center is used as an anchor point for the transformation
    def transform(self, matrix: TransformationMatrix, center=None):
        center = self.get_origin() if center is None else center
        self.primitive.transform(matrix, center)

    def get_lod(self) -> str:
        return self.lod

    def get_vertices(self, flatten=False):
        return self.primitive.get_vertices(flatten)

    def duplicate(self) -> CityGeometry:
        return GeometryPrimitive(self.primitive.copy(), self.lod)

    def get_origin(self):
        g_min, g_max = self.get_min_max()
        return [
            (g_min[0] + g_max[0]) / 2, 
            (g_min[1] + g_max[1]) / 2, 
            g_min[2]
        ]

    def to_geometry_primitive(self) -> 'GeometryPrimitive':
        return self

    def to_cj(self, city) -> dict:
        citygeometry = {
            'type': self.primitive.get_type(),
            'lod': self.lod,
            'boundaries': self.primitive.index_vertices(city.vertices)
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

    # center is in self.matrix
    def transform(self, matrix: TransformationMatrix, center=None):
        self.matrix = self.matrix.dot(matrix)

    def get_lod(self) -> str:
        return self.geometry.get_lod()

    def get_vertices(self, flatten=False):
        vertices = self.geometry.get_vertices(flatten)
        return self.matrix.reproject_vertices(vertices)

    def duplicate(self) -> CityGeometry:
        return GeometryInstance(self.geometry, self.matrix.copy())

    def get_origin(self):
        return self.matrix.get_origin()

    def to_geometry_primitive(self) -> GeometryPrimitive:
        primitive = self.geometry.primitive.copy()
        primitive.transform(self.matrix)
        return GeometryPrimitive(primitive, self.geometry.lod)

    def to_cj(self, city) -> dict:
        boundary = city.vertices.add(self.matrix.get_origin())
        template_index = city.geometry_templates.add_template(self.geometry)

        cityinstance = {
            'type': 'GeometryInstance',
            'template': template_index,
            'boundaries': [boundary],
            'transformationMatrix': self.matrix.recenter().to_cj()
        }
        return cityinstance

