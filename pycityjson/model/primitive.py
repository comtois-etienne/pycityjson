# https://www.cityjson.org/dev/geom-arrays/


import numpy as np

from .appearance import Material
from .matrix import TransformationMatrix
from .semantic import Semantic
from .vertices import Vertex, Vertices


class Primitive:
    """
    A Primitive is a basic element of the geometry.
    It is store in a GeometryPrimitive
    """

    def get_children(self) -> list['Primitive'] | list['Point']:
        """
        List of Primitive for all class except for MultiPoint which can have Point as children
        :return: list of children of the primitive
        """
        return self.children

    def __str__(self):
        return f'{self.get_type()}(len={len(self.children)})'

    def __repr__(self) -> str:
        children = ', '.join([repr(child) for child in self.children])
        return f'{self.get_type()}({children})'

    def transform(self, matrix: TransformationMatrix, center=[0, 0, 0]) -> None:
        """
        Applies a transformation matrix to all the children of the primitive (recursively)
        :param matrix: TransformationMatrix to apply to the geometry
        :param center: The center of the transformation (default is the origin (0, 0, 0))
        """
        for child in self.children:
            child.transform(matrix, center)

    def get_type(self) -> str:
        """
        :return: the type of the primitive - the name of the class or its alias
        """
        return self.type

    def copy(self) -> 'Primitive':
        """
        Deep copy of the primitive
        :return: a new instance of the primitive with a deep copy of the children
        """
        return self.__class__([child.copy() for child in self.children])

    def add_child(self, child: 'Primitive') -> None:
        """
        Adds a child to the primitive - Should be the class of the children's Primitive
        Always a Primitive except for the MultiPoint which can have Point as children
        :param child: Primitive to add to the children (Point for MultiPoint)
        """
        self.children.append(child)

    def index_vertices(self, vertices: Vertices) -> list:
        """
        Returns the indexes of the vertices in the Vertices object
        Runs recursively on the children until it reaches the Point
        :param vertices: Vertices object to index the vertices
        :return: list of indexes of the vertices in the Vertices object to be used in the boundaries
        """
        return [child.index_vertices(vertices) for child in self.children]

    def get_vertices(self, flatten=False) -> list:
        """
        Returns the vertices of the primitive
        :param flatten: If True, the vertices are returned as a list of Vertex, else as the original structure of the geometry
        :return: list of vertices of the primitive
        """
        vertices = []
        for child in self.children:
            if flatten:
                vertices += child.get_vertices(flatten)
            else:
                vertices.append(child.get_vertices(flatten))
        return vertices

    def get_min_max(self) -> tuple[Vertex, Vertex]:
        """
        Returns the minimum and maximum vertices of the primitive
        Represents the bounding box of the primitive
        :return: Tuple of two vertex with the minimum and maximum coordinates as [min_x, min_y, min_z] and [max_x, max_y, max_z]
        """
        vertices = self.get_vertices(flatten=True)
        vertices = np.array(vertices)
        v_min = np.min(vertices, axis=0)
        v_max = np.max(vertices, axis=0)
        return v_min.tolist(), v_max.tolist()

    def normalize(self, centered=False) -> None:
        """
        Transforms the primitive to a normalized form
        The primitive is scaled to fit in a unit cube (1.0, 1.0, 1.0) (not uniform scaling)
        The origin of the primitive can be centered at the bottom of the unit cube or at the origin (0, 0, 0)
        This is usefull to be used in a GeometryPrimitive
        :param centered: If True, the origin of the primitive is centered at the bottom of the unit cube, else at the origin (0, 0, 0) (minimum coordinates)
        :return: None - the primitive is modified
        """
        _min, _ = self.get_min_max()
        matrix = TransformationMatrix().translate([-_min[0], -_min[1], -_min[2]])
        self.transform(matrix)

        _min, _max = self.get_min_max()
        scale = [
            1 / (_max[0] - _min[0]),
            1 / (_max[1] - _min[1]),
            1 / (_max[2] - _min[2]),
        ]
        matrix = TransformationMatrix().scale(scale)
        self.transform(matrix)

        if centered:
            matrix = TransformationMatrix().translate([-0.5, -0.5, 0])
            self.transform(matrix)

    def get_semantic_surfaces(self) -> list[dict]:
        """
        Super method that should be overridden
        returns the semantic of the surfaces of the primitive
        :return: list of semantic of the surfaces of the primitive
        """
        return None

    def get_semantic_values(self, semantics: list[dict]) -> list[int]:
        """
        Returns the index of the semantic in the list of semantics
        Recursively runs on the children until it reaches the MultiLineString
        :param semantics: list of semantics to compare - see self.get_semantic_surfaces()
        :return: list of indexes of the semantics in the list of semantics
        """
        return [child.get_semantic_values(semantics) for child in self.children]


class Point:
    """
    A Point represents a vertex.
    When converted to boundaries, the index of the vertex in Vertices is used.

    It cannot be stored directly in the geometry of the CityJSON file.
    It must be stored in a MultiPoint
    """

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __repr__(self):
        return f'Point({self.x}, {self.y}, {self.z})'

    def copy(self) -> 'Point':
        """
        Deep copy of the point
        :return: a new instance of the point with the same coordinates
        """
        return self.__class__(self.x, self.y, self.z)

    def transform(self, matrix: TransformationMatrix, center=[0, 0, 0]):
        """
        Applies a transformation matrix to the point
        :param matrix: TransformationMatrix to apply to the point
        :param center: The center of the transformation (default is the origin (0, 0, 0))
        :return: None - the point is modified
        """
        vertex = [self.x - center[0], self.y - center[1], self.z - center[2]]
        vertex = matrix.reproject_vertex(vertex)
        self.x = vertex[0] + center[0]
        self.y = vertex[1] + center[1]
        self.z = vertex[2] + center[2]

    def to_list(self) -> Vertex:
        """
        :return: List of the coordinates of the point (x, y, z)
        """
        return [self.x, self.y, self.z]

    def index_vertices(self, vertices: Vertices) -> int:
        """
        Adds the vertex to the Vertices object and returns its index
        :param vertices: Vertices object to add the vertex to
        :return: index of the vertex in the Vertices object
        """
        index = vertices.add(self.to_list())
        return index


# collection of points -> used to create shape
class MultiPoint(Primitive):
    """
    A MultiPoint represents a ring (triangle, square, etc.)
    A MultiPoint is a collection of points.
    When converted to boundaries, the depth of the array is 1. (array of indexes)

    The first point does not repeat at the end of the array.

    Should be stored in a MultiLineString which is stored in a MultiSurface for visualisation
    Can still be stored directly in the CityJSON file if visualisation is not needed (ex.: point cloud)
    """

    __ptype = 'MultiPoint'

    def __init__(self, points: list[Point] = None):
        self.type = self.__ptype
        self.children = [] if points is None else points

    def get_vertices(self, flatten=False) -> list[Vertex]:
        """
        :param flatten: not used - always returns the list of points
        :return: list of Vertex
        """
        return [point.to_list() for point in self.children]

    def get_semantic_values(self, semantics):
        """
        MultiPoint doesn't have a semantic
        """
        return None

    def add_child(self, child: Point) -> None:
        """
        Same as super.add_child() but with a Point as a child
        :param child: Point to add to the children
        """
        return self.children.append(child)


class MultiLineString(Primitive):
    """
    A MultiLineString represents a suface (ex.: a door face, a wall face).
    A MultiLineString is a collection of MultiPoints (rings).
    When converted to boundaries, the depth of the array is 2.

    The first MultiPoint is the exterior ring, the rest are interior rings of the surface.
    The subsequent MultiPoints are holes in the surface.

    Should be stored in a MultiSurface for visualisation
    Can still be stored directly in the CityJSON file if visualisation is not needed

    ------ Semantic ------
    Semantic is used to describe the surface - not mandatory.
    It can describe the surface more precisely than with the semantic (type) given by the CityObject
    (ex.: for a CityObject that is a Building - one MultiLineString can be a wall face with the WallSurface semantic).

    ------ Materials ------
    Material is used to display the surface - not mandatory.
    It can have multiple themes (ex.: visual, thermal...) with a Material for each theme.
    """

    __ptype = 'MultiLineString'

    def __init__(self, faces: list[MultiPoint] = None, semantic: Semantic = None, materials: dict = None):
        self.type = self.__ptype
        self.children = [] if faces is None else faces

        self.semantic = semantic
        self.__materials = {} if materials is None else materials

    def __repr__(self):
        if self.semantic is None:
            return super().__repr__()
        children = ', '.join([repr(child) for child in self.children])
        semantic = self.semantic.to_dict()
        return f'{self.get_type()}((Semantic({semantic}))=({children}))'

    def set_exterior_face(self, exterior: MultiPoint):
        """
        Sets the ring that represents the face of the surface
        Use .add_child() to add holes in the surface
        :param exterior: MultiPoint that represents the face of the surface
        """
        if len(self.children) == 0:
            self.children.append(exterior)
        else:
            self.children[0] = exterior

    def set_material(self, material: Material, theme: str = 'visual'):
        self.__materials[theme] = material

    def get_material(self, theme: str = 'visual') -> Material | None:
        if theme in self.__materials:
            return self.__materials[theme]
        return None

    def get_semantic_cj(self) -> dict | None:
        """
        Converts the semantic to a dictionary if it exists
        """
        return self.semantic.to_dict() if self.semantic is not None else None

    def get_semantic_values(self, semantics: list[dict]) -> int | None:
        """
        :param semantics: list of semantics
        :return: index of the semantic in the list of semantics
        """
        for i in range(len(semantics)):
            if semantics[i] == self.semantic:
                return i
        return None


# Used to create a landscape of a building wall
class MultiSurface(Primitive):
    """
    A MultiSurface represents a collection of surfaces (ex.: a wall, a terrain model).
    A MultiSurface is a collection of MultiLineStrings (surface).
    When converted to boundaries, the depth of the array is 3.
    Have an alternative representation as a CompositeSurface.
    """

    __ptype = 'MultiSurface'  # separate surfaces with holes
    __ptype_a = 'MultiSurface'  # separate surfaces with holes
    __ptype_b = 'CompositeSurface'  # adjacents surfaces without overlap

    def __init__(self, surfaces: list[MultiLineString] = None):
        self.type = self.__ptype
        self.children = [] if surfaces is None else surfaces

    def get_semantic_surfaces(self) -> list[dict]:
        """
        :return: list of semantic of the surfaces of the primitive
        """
        semantics = {}
        for surface in self.children:
            semantic = surface.get_semantic_cj()
            if semantic is None:
                return None
            semantics[surface.semantic['uuid']] = semantic
        return list(semantics.values())


# Used to create a building
class Solid(Primitive):
    """
    A Solid represents a volume (ex.: a building).
    A Solid is a collection of MultiSurfaces (collection of surfaces).
    When converted to boundaries, the depth of the array is 4.
    """

    __ptype = 'Solid'

    def __init__(self, multi_surfaces: list[MultiSurface] = None):
        self.type = self.__ptype
        self.children = [] if multi_surfaces is None else multi_surfaces

    def get_semantic_surfaces(self) -> list[dict]:
        """
        :return: list of semantic of the surfaces of the primitive
        """
        semantics = {}
        for multi_surface in self.children:
            for surface in multi_surface.children:
                semantic = surface.get_semantic_cj()
                if semantic is None:
                    return None
                semantics[surface.semantic['uuid']] = semantic
        return list(semantics.values())


class MultiSolid(Primitive):
    """
    A MultiSolid represents a collection of volumes (ex.: a building and its shed).
    A MultiSolid is a collection of Solids (volume).
    When converted to boundaries, the depth of the array is 5.
    Have an alternative representation as a CompositeSolid.
    """

    __ptype = 'MultiSolid'
    __ptype_a = 'MultiSolid'  # separate solids
    __ptype_b = 'CompositeSolid'  # adjacents solids

    def __init__(self, solids: list[Solid] = None):
        self.type = self.__ptype
        self.children = [] if solids is None else solids

    def get_semantic_surfaces(self) -> list[dict]:
        """
        :return: list of semantic of the surfaces of the primitive
        """
        semantics = {}
        for solid in self.children:
            for multi_surface in solid.children:
                for surface in multi_surface.children:
                    semantic = surface.get_semantic_cj()
                    if semantic is None:
                        return None
                    semantics[surface.semantic['uuid']] = semantic
        return list(semantics.values())
