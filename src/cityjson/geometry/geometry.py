from .primitive.primitive import Primitive


class CityGeometry:
    def to_cj(self, vertices):
        pass

    def set_lod(self, lod):
        self.lod = lod

    def get_lod(self):
        return self.lod

    def get_boundaries(self):
        pass

    def get_vertices(self, flat=False):
        pass

    def get_max(self, axis=0):
        pass

    def get_min(self, axis=0):
        pass


# Contains MultiSolid, Solid, MultiSurface, MultiLineString...
class CityPrimitive(CityGeometry):
    def __init__(self, primitive: Primitive, lod: str = '1'):
        self.primitive = primitive
        self.set_lod(lod)

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


# Contains GeometryInstance (Template)
class CityInstance(CityGeometry):
    #todo
    pass

