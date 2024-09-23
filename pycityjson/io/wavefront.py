import numpy as np

from .cityjson import *
from ..model.primitive import *


class WavefrontSerializer:
    def __init__(self, city: City):
        self.city = city
        self.vertices = Vertices()
        self.vertices.start_index = 1
        self.wavefront = [] # list of strings
        self.current_type = ''
        self.precision = 10**(self.city.precision())
        self.as_one_geometry = False

    def _vertices_to_wavefront(self):
        vertices = self.vertices.tolist()
        return [f'v {x} {y} {z}' for x, y, z in vertices]

    def _serialize_multi_line_string(self, multi_line_string: MultiLineString):
        children = multi_line_string.children
        exterior_shape = children[0].get_vertices()
        exterior_shape = np.array(exterior_shape) * self.precision
        exterior_shape = exterior_shape.round().astype(int).tolist()
        # todo: holes
        indexes = [self.vertices.add(vertice) for vertice in exterior_shape]
        self.wavefront.append(f'f {" ".join(map(str, indexes))}')
    
    def _serialize_multi_surface(self, multi_surface: MultiSurface):
        for child in multi_surface.children:
            self._serialize_multi_line_string(child)
    
    def _serialize_solid(self, solid: Solid):
        for child in solid.children:
            self._serialize_multi_surface(child)
    
    def _serialize_multi_solid(self, multi_solid: MultiSolid):
        for child in multi_solid.children:
            self._serialize_solid(child)

    def _serialize_primitive(self, primitive: Primitive):
        # todo : I hate this
        if isinstance(primitive, MultiLineString):
            self._serialize_multi_line_string(primitive)
        if isinstance(primitive, MultiSurface):
            self._serialize_multi_surface(primitive)
        if isinstance(primitive, Solid):
            self._serialize_solid(primitive)
        if isinstance(primitive, MultiSolid):
            self._serialize_multi_solid(primitive)

    def _serialize_geometry(self, geometry: CityGeometry):
        geometry = geometry.to_geometry_primitive()
        if not self.as_one_geometry:
            lod = geometry.get_lod().strip().replace(' ', '_')
            lod = lod if lod.startswith('lod') else f'lod_{lod}'
            self.wavefront.append(f'g {lod}')
            self.wavefront.append(f'usemtl {self.current_type}') # todo use material in the cityjson file
        self._serialize_primitive(geometry.primitive)

    def _serialize_cityobject(self, city_objects: CityObject):
        self.current_type = city_objects.type
        if not self.as_one_geometry:
            self.wavefront.append(f'o {city_objects.uuid()} {self.current_type}')
        for geometry in city_objects.geometries:
            self._serialize_geometry(geometry)

    def _serialize_city(self):
        for city_object in self.city.cityobjects._cityobjects:
            if city_object.type == 'CityObjectGroup':
                pass
            self.wavefront.append('')
            self._serialize_cityobject(city_object)

        material = [f'mtllib cityjson.mtl'] # todo use material in the cityjson file
        vertices = self._vertices_to_wavefront()
        return material + [''] + vertices + self.wavefront

    def serialize(self, as_one_geometry=False) -> list[str]:
        self.as_one_geometry = as_one_geometry
        if as_one_geometry:
            self.wavefront.append('')
            self.wavefront.append('g cityjson')
        return self._serialize_city()

