from shapely.geometry import Polygon
from shapely.ops import triangulate
import numpy as np

from .cityjson import *
from ..model.primitive import *


def triangles_within(triangles, polygon):
    return [triangle for triangle in triangles if triangle.within(polygon)]


def triangles_to_list(triangulated):
    triangles = np.array([list(triangle.exterior.coords) for triangle in triangulated])
    # drop last point as it is the same as the first one
    triangles = np.array([np.array(triangle[:-1]) for triangle in triangles])
    return triangles


def find_closest_point(point, points):
    distances = np.linalg.norm(points - point, axis=1)
    closest_idx = np.argmin(distances)
    return points[closest_idx]


def all_permutations(points : np.ndarray):
    return np.array([np.roll(points, i, axis=0) for i in range(len(points))])


def add_missing_triangle(triangles, triangle):
    coords = np.array(list(triangle.exterior.coords))[:-1]
    all_perms = all_permutations(coords)
    for perm in all_perms:
        tri_perm = Polygon(perm)
        if tri_perm in triangles:
            break
    else:
        triangles.append(triangle)


def add_missing_triangles(exterior_shape, interior_shapes, triangles):
    for hole in interior_shapes:
        hole = np.array(hole)
        centers = (hole[:-1] + hole[1:]) / 2
        closest = np.array([find_closest_point(center, exterior_shape) for center in centers])
        polygons = np.array([Polygon([a, b, c]) for a, b, c in zip(hole[:-1], hole[1:], closest)])
        tris = np.array([triangulate(poly)[0] for poly in polygons])
        for tri in tris:
            add_missing_triangle(triangles, tri)


def triangulate_rings(exterior_shape, interior_shapes):
    polygon = Polygon(exterior_shape, holes=interior_shapes)
    triangles = triangulate(polygon)
    add_missing_triangles(exterior_shape, interior_shapes, triangles)
    triangles = triangles_within(triangles, polygon)
    triangles_list = triangles_to_list(triangles)
    return triangles_list, triangles


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
        # todo semantics
        # todo holes
        # interior_shapes = [child.get_vertices() for child in children[1:]]
        # triangles, _ = triangulate_rings(interior_shapes, exterior_shape)
        # for triangle in triangles:
            # indexes = [self.vertices.add(vertice) for vertice in triangle]
            # self.wavefront.append(f'f {indexes[0]} {indexes[1]} {indexes[2]}')
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

