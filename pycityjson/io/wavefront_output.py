import numpy as np

from pycityjson.model import City, CityObject, TransformationMatrix, Vertices
from pycityjson.obj import WavefrontObject


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

    def __serialize_cityobject(self, city_object: CityObject):
        self.__current_type = city_object.type
        wavefront_object = WavefrontObject.from_city_object(city_object)
        if not self.__as_one_geometry:
            self.__wavefront.append(
                f'o {wavefront_object.name} {wavefront_object.sub_name}',
            )
        for group in wavefront_object.groups:
            if not self.__as_one_geometry:
                self.__wavefront.append(f'g {group.name}')
                self.__wavefront.append(f'usemtl {self.__current_type}')
            for face in group.faces:
                exterior_shape = np.array([
                    [vertex.x, vertex.y, vertex.z]
                    for vertex in face.vertices
                ]) * self.__precision
                exterior_shape = exterior_shape.round().astype(int).tolist()
                indexes = [self.__vertices.add(vertex) for vertex in exterior_shape]
                self.__wavefront.append(f'f {" ".join(map(str, indexes))}')

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
