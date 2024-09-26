import numpy as np

from pycityjson.model import City, CityGeometry, CityObject, MultiLineString, MultiSolid, MultiSurface, Primitive, Solid, TransformationMatrix, Vertices


class WavefrontSerializer:
    def __init__(self, city: City):
        self.__city: City = city
        self.__vertices = Vertices(precision=city.precision())
        self.__vertices.start_index = 1  # Wavefront obj indexes start at 1
        self.__wavefront: list[str] = []
        self.__current_type = ''
        self.__precision: int = 10 ** (self.__city.precision())
        self.__as_one_geometry = False
        self.__swap_yz = False

    def __vertices_to_wavefront(self):
        vertices = self.__vertices.tolist()
        if self.__swap_yz:
            matrix = TransformationMatrix().rotate_x(90)
            vertices = matrix.reproject_vertices(vertices)
        return [f'v {x} {y} {z}' for x, y, z in vertices]

    def __serialize_multi_line_string(self, multi_line_string: MultiLineString):
        children = multi_line_string.children
        exterior_shape = children[0].get_vertices()
        exterior_shape = np.array(exterior_shape) * self.__precision
        exterior_shape = exterior_shape.round().astype(int).tolist()
        # todo: holes
        indexes = [self.__vertices.add(vertex) for vertex in exterior_shape]
        self.__wavefront.append(f'f {" ".join(map(str, indexes))}')

    def __serialize_multi_surface(self, multi_surface: MultiSurface):
        for child in multi_surface.children:
            self.__serialize_multi_line_string(child)

    def __serialize_solid(self, solid: Solid):
        for child in solid.children:
            self.__serialize_multi_surface(child)

    def __serialize_multi_solid(self, multi_solid: MultiSolid):
        for child in multi_solid.children:
            self.__serialize_solid(child)

    def __serialize_primitive(self, primitive: Primitive):
        # todo : I hate this
        if isinstance(primitive, MultiLineString):
            self.__serialize_multi_line_string(primitive)
        if isinstance(primitive, MultiSurface):
            self.__serialize_multi_surface(primitive)
        if isinstance(primitive, Solid):
            self.__serialize_solid(primitive)
        if isinstance(primitive, MultiSolid):
            self.__serialize_multi_solid(primitive)

    def __serialize_geometry(self, geometry: CityGeometry):
        geometry = geometry.to_geometry_primitive()
        if not self.__as_one_geometry:
            lod = geometry.get_lod().strip().replace(' ', '_')
            lod = lod if lod.startswith('lod') else f'lod_{lod}'
            self.__wavefront.append(f'g {lod}')
            self.__wavefront.append(f'usemtl {self.__current_type}')  # todo use material in the cityjson file
        self.__serialize_primitive(geometry.primitive)

    def __serialize_cityobject(self, city_object: CityObject):
        self.__current_type = city_object.type
        if not self.__as_one_geometry:
            self.__wavefront.append(f'o {city_object.uuid()} {self.__current_type}')
        for geometry in city_object.geometries:
            self.__serialize_geometry(geometry)

    def __serialize_city(self):
        for city_object in self.__city.cityobjects:
            if city_object.type == 'CityObjectGroup':
                pass
            self.__wavefront.append('')
            self.__serialize_cityobject(city_object)

        material = ['mtllib cityjson.mtl']  # todo use material in the cityjson file
        vertices = self.__vertices_to_wavefront()
        return material + [''] + vertices + self.__wavefront

    def serialize(self, *, as_one_geometry=False, swap_yz=False) -> list[str]:
        """
        Converts the City into a Wavefront OBJ file.
        Each CityObject is converted into a `o` with its UUID and type.
        Each CityGeometry is converted into a `g` with its LOD.
        The type of the CityObject is used as the material name.
        The type of the surfaces (muli_line_string) are not supported yet.
        The materials in the CityJSON file are not supported yet.
        The holes in the geometries are not supported yet.
        :param as_one_geometry: If True, all cityobjects geometries are merged into a single geometry.
        :param swap_yz: If True, the Y and Z coordinates are swapped for obj visualization.
        """
        self.__as_one_geometry = as_one_geometry
        self.__swap_yz = swap_yz
        if as_one_geometry:
            self.__wavefront.append('')
            self.__wavefront.append('g cityjson')
        return self.__serialize_city()
