from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pycityjson.model import CityObject, CityObjects, Material


@dataclass
class WavefrontVertex:
    """
    :param x: X coordinate of the vertex
    :param y: Y coordinate of the vertex
    :param z: Z coordinate of the vertex
    """
    x: float
    y: float
    z: float
    
    def xyz(self) -> str:
        """
        :return: String representing the vertex in the Wavefront OBJ format
        """
        return f"v {self.x} {self.y} {self.z}"
    
    def xzy(self) -> str:
        """
        :return: String representing the vertex in the Wavefront OBJ format with swapped y and z coordinates
        """
        return f"v {self.x} {self.z} {self.y}"
    
    def round(self, precision: int = 3) -> 'WavefrontVertex':
        return WavefrontVertex(
            round(self.x, precision),
            round(self.y, precision),
            round(self.z, precision),
        )
    
    def __eq__(self, other: 'WavefrontVertex') -> bool:
        if not isinstance(other, WavefrontVertex):
            return False
        return (
            self.x == other.x and
            self.y == other.y and
            self.z == other.z
        )
    
    def __add__(self, other: 'WavefrontVertex') -> 'WavefrontVertex':
        if not isinstance(other, WavefrontVertex):
            raise TypeError(f"Cannot add {type(other)} to WavefrontVertex")
        return WavefrontVertex(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )
    
    def __sub__(self, other: 'WavefrontVertex') -> 'WavefrontVertex':
        if not isinstance(other, WavefrontVertex):
            raise TypeError(f"Cannot subtract {type(other)} from WavefrontVertex")
        return WavefrontVertex(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )


class WavefrontVertices:
    """
    :param precision: Precision of the vertices in the collection. If None, no rounding is done.
    :param vertices_list: List of vertices in the collection - without duplicates
    :param vertices_dict: Dict to store the index of the vertices for performance reasons
    """

    def __init__(self, precision: int = None):
        self.__precision = precision
        self.__vertices_list : list[WavefrontVertex] = []
        self.__vertices_dict: dict[str, int] = {}

    def __contains__(self, item: WavefrontVertex) -> bool:
        """
        :param item: Vertex to check if it is in the collection
        :return: True if the vertex is in the collection, False otherwise
        """
        if not isinstance(item, WavefrontVertex):
            return False
        return item.xyz() in self.__vertices_dict

    def add(self, vertex: WavefrontVertex) -> int:
        """
        Add a vertex to the collection with a given precision. Will round the vertex to the precision given in the
        constructor.
        """
        vertex = vertex if self.__precision is None else vertex.round(self.__precision)

        if vertex not in self:
            self.__vertices_dict[vertex.xyz()] = len(self.__vertices_list) + 1
            self.__vertices_list.append(vertex)

        return self.get_index(vertex)
    
    def get_index(self, vertex: WavefrontVertex) -> int | None:
        """
        :param vertex: Vertex to get the index of
        :return: Index of the vertex in the collection. None if the vertex is not in the collection
        """
        if vertex not in self:
            return None
        return self.__vertices_dict[vertex.xyz()]
    
    def serialize(self, swap_yz=False) -> list[str]:
        """
        Serialize the vertices to a list of string in the Wavefront OBJ format.
        :param swap_yz: If True, swap the y and z coordinates
        :return: List of strings representing the vertices in the Wavefront OBJ format
        """
        return [v.xzy() if swap_yz else v.xyz() for v in self.__vertices_list]


@dataclass
class WavefrontFace:
    """
    Example: `f 113 114 115 116 117 118`
    :param vertices: List of vertices in the face
    """
    vertices: list[WavefrontVertex]

    def serialize(self, vertices: WavefrontVertices) -> str:
        """
        Serialize the face to a string in the Wavefront OBJ format.
        :param vertices: Collection of vertices to get the index of the vertices
        :return: String representing the face in the Wavefront OBJ format
        """
        indexes = [str(vertices.add(v)) for v in self.vertices]
        return f"f {' '.join(indexes)}"

    def to_city_surface(self):
        """Convert this face into a CityJSON surface."""
        from pycityjson.model import MultiLineString, MultiPoint, Point

        return MultiLineString([
            MultiPoint([Point(vertex.x, vertex.y, vertex.z) for vertex in self.vertices]),
        ])
    
    def translate(self, vertex: WavefrontVertex) -> 'WavefrontFace':
        """
        Translate the face by a given vertex.
        :param vertex: Vertex to translate the face by
        :return: New translated face
        """
        translated_vertices = [v + vertex for v in self.vertices]
        return WavefrontFace(translated_vertices)


@dataclass
class WavefrontGroup:
    """
    :param name: Name of the geometry group (LoD)
    :param faces: List of faces in the group
    """
    name: str
    faces: list[WavefrontFace]

    def serialize(self, vertices: WavefrontVertices) -> list[str]:
        """
        Serialize the group to a list of string in the Wavefront OBJ format.
        :param vertices: Collection of vertices to get the index of the vertices
        :return: List of strings representing the group in the Wavefront OBJ format
        """
        serialized_faces = [face.serialize(vertices) for face in self.faces]
        return [f"g {self.name}"] + serialized_faces
    
    def from_indexes_and_vertices(
        name: str,
        indexes: list[list[int]],
        vertices: list[list[float]],
    ) -> 'WavefrontGroup':
        """
        Create a group from a list of indexes and vertices.
        :param indexes: List of indexes of the vertices forming the faces
        :param vertices: List of vertices
        """
        faces: list[WavefrontFace] = []
        for f in indexes:
            face: list[WavefrontVertex] = []
            for i in f:
                vertex = WavefrontVertex(vertices[i][0], vertices[i][1], vertices[i][2])
                face.append(vertex)
            faces.append(WavefrontFace(face))
        
        return WavefrontGroup(name, faces)

    def to_city_geometry(
        self,
        material: 'Material | None' = None,
        lod: str | int | None = None,
    ):
        """Convert this group into a CityJSON geometry."""
        from pycityjson.model import GeometryPrimitive, MultiSurface

        surfaces = [face.to_city_surface() for face in self.faces]
        if material is not None:
            for surface in surfaces:
                surface.set_material(material)
        return GeometryPrimitive(
            MultiSurface(surfaces),
            self.name if lod is None else str(lod),
        )
    
    def translate(self, vertex: WavefrontVertex) -> 'WavefrontGroup':
        """
        Translate the group by a given vertex.
        :param vertex: Vertex to translate the group by
        :return: New translated group
        """
        translated_faces = [face.translate(vertex) for face in self.faces]
        return WavefrontGroup(self.name, translated_faces)


@dataclass
class WavefrontObject:
    """
    :param name: UUID of the nDSM combined with the mask id
    :param sub_name: CityJSON class name (semantic)
    :param groups: Geometries at different levels of detail (LoD) for the same object
    """
    name: str
    sub_name: str | None
    groups: list[WavefrontGroup]

    @classmethod
    def from_city_object(cls, city_object: 'CityObject') -> 'WavefrontObject':
        """Convert a CityJSON object to its Wavefront representation."""
        groups: list[WavefrontGroup] = []
        for geometry in city_object.geometries:
            primitive = geometry.to_geometry_primitive()
            faces = [
                WavefrontFace([
                    WavefrontVertex(*vertex)
                    for vertex in surface.get_vertices(flatten=True)
                ])
                for surface in primitive.get_surfaces()
            ]
            groups.append(WavefrontGroup(f'lod_{primitive.get_lod()}', faces))
        return cls(city_object.uuid(), city_object.type, groups)

    def to_city_object(
        self,
        cityobjects: 'CityObjects',
        object_type: str | None = None,
        material: 'Material | None' = None,
    ) -> 'CityObject':
        """Convert this Wavefront object to a CityJSON object."""
        from pycityjson.model import CityObject

        city_object = CityObject(
            cityobjects,
            object_type or self.sub_name or 'GenericCityObject',
            uuid=self.name,
        )
        for group in self.groups:
            city_object.add_geometry(group.to_city_geometry(material))
        return city_object

    def serialize(self, vertices: WavefrontVertices) -> list[str]:
        """
        Serialize the object to a list of string in the Wavefront OBJ format.
        :param vertices: Collection of vertices to get the index of the vertices
        :return: List of strings representing the object in the Wavefront OBJ format
        """
        object_header = f"o {self.name}" if self.sub_name is None else f"o {self.name} {self.sub_name}"
        serialized_groups = []
        for group in self.groups:
            serialized_groups += group.serialize(vertices)

        return [object_header] + serialized_groups


def serialize_wavefront(wavefront_objects: list[WavefrontObject], precision=None, swap_yz=False) -> list[str]:
    vertices = WavefrontVertices(precision=precision)
    serialized_objects = []

    for obj in wavefront_objects:
        serialized_object = obj.serialize(vertices)
        serialized_objects += serialized_object
        serialized_objects.append('') # Add an empty line between objects

    return vertices.serialize(swap_yz) + [''] + serialized_objects


def write_wavefront(wavefront_objects: list[WavefrontObject], file_path: str, precision=None, swap_yz=False) -> None:
    """
    Write a list of Wavefront objects to a file.
    :param wavefront_objects: List of Wavefront objects to write
    :param path: Path to the file to write
    :param swap_yz: If True, swap the y and z coordinates
    """
    wavefront_str: list[str] = serialize_wavefront(wavefront_objects, precision, swap_yz)
    with open(file_path, 'w') as wavefront_file:
        for line in wavefront_str:
            wavefront_file.write(f'{line}\n')
