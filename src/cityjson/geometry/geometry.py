from .primitive.primitive import Primitive


# Contains MultiSolid, Solid, MultiSurface, MultiLineString...
class CityGeometry:
    def __init__(self, primitive: Primitive, lod: str = '1'):
        self.primitive = primitive
        self.lod = lod

    def __str__(self) -> str:
        return f'{self.primitive.get_type()}(lod {self.lod})'

    def __repr__(self) -> str:
        return f'CityGeometry((lod({self.lod}))({repr(self.primitive)}))'
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, CityGeometry):
            return False
        return self.__repr__() == repr(value)
    
    def get_boundaries(self):
        # todo
        pass

    def get_vertices(self):
        return self.primitive.get_vertices()

    def get_max(self, axis=0):
        # todo
        pass

    def get_min(self, axis=0):
        # todo
        pass

    def to_cj(self, vertices):
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

