import numpy as np

from .matrix import TransformationMatrix
from .primitive import Primitive
from .vertices import Vertex


class CityGeometry:
    def transform(self, matrix: TransformationMatrix, center=None) -> None:
        """
        Super method to apply the transformation matrix to the geometry
        See the implementation in GeometryPrimitive and GeometryInstance
        :param matrix: TransformationMatrix to apply to the geometry
        :param center: The center of the transformation - Not used by GeometryPrimitive
        """
        pass

    def get_lod(self) -> str:
        """
        Super method that should be overridden by GeometryPrimitive and GeometryInstance
        :return: The level of detail of the geometry
        """
        pass

    def get_vertices(self, flatten:bool) -> list:
        """
        Returns the vertices of the geometry as a list of Vertex or as the original structure of the geometry
        :param flatten: If True, the vertices are returned as a list of Vertex, else as the original structure of the geometry
        """
        pass

    def get_min_max(self) -> tuple[Vertex, Vertex]:
        """
        Returns the minimum and maximum coordinates of the geometry
        Represents the bounding box of the geometry
        :return: Tuple of two vertex with the minimum and maximum coordinates as [min_x, min_y, min_z] and [max_x, max_y, max_z]
        """
        vertices = self.get_vertices(flatten=True)
        vertices = np.array(vertices)
        v_min = np.min(vertices, axis=0)
        v_max = np.max(vertices, axis=0)
        return v_min.tolist(), v_max.tolist()

    def duplicate(self) -> 'CityGeometry':
        """
        Super method that should be overridden by GeometryPrimitive and GeometryInstance
        Different than copy - see each implementation
        """
        pass

    def get_origin(self) -> Vertex:
        """
        Super method that should be overridden by GeometryPrimitive and GeometryInstance
        """
        pass

    def is_geometry_primitive(self) -> bool:
        """
        Helper method to check if the geometry is a GeometryPrimitive
        """
        return isinstance(self, GeometryPrimitive)

    def is_geometry_instance(self) -> bool:
        """
        Helper method to check if the geometry is a GeometryInstance
        """
        return isinstance(self, GeometryInstance)

    def to_geometry_primitive(self) -> 'GeometryPrimitive':
        """
        Super method that should be overridden by GeometryInstance
        """
        return self

    # def to_geometry_instance(self) -> 'GeometryInstance':
    #     # todo
    #     pass


# Contains MultiSolid, Solid, MultiSurface, MultiLineString...
class GeometryPrimitive(CityGeometry):
    def __init__(self, primitive: Primitive, lod: str = '1'):
        self.primitive : Primitive = primitive
        self.lod : str = lod # level of detail (1, 2, 3, ...)

    def __str__(self) -> str:
        return f'Geometry{self.primitive.get_type()}(lod={self.lod})'

    def __repr__(self) -> str:
        return f'Geometry((lod({self.lod}))({repr(self.primitive)}))'

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, GeometryPrimitive):
            return False
        return self.__repr__() == repr(value)

    def transform(self, matrix: TransformationMatrix, center=None) -> None:
        """
        GeometryPrimitive doens't have a transformation matrix
        Center is used as an anchor point for the transformation
        The center of the base of the geometry is used as the anchor point if center is None
        The transformation will modify the geometry in place - it should not be shared with other GeometryPrimitives
        :param matrix: TransformationMatrix to apply to the geometry
        :param center: The center of the transformation
        """
        center = self.get_origin() if center is None else center
        self.primitive.transform(matrix, center)

    def get_lod(self) -> str:
        """
        :return: The level of detail of the geometry
        """
        return self.lod

    def get_vertices(self, flatten=False) -> list:
        """
        :param flatten: If True, the vertices are returned as a list of Vertex, else as the original structure of the geometry
        """
        return self.primitive.get_vertices(flatten)

    def duplicate(self) -> CityGeometry:
        """
        :return: A new GeometryPrimitive with a deep copy of the primitive
        """
        return GeometryPrimitive(self.primitive.copy(), self.lod)

    def get_origin(self) -> Vertex:
        """
        Note : use .get_min_max() if you need the corner of the bounding box
        :return: The center of the base of the geometry
        """
        g_min, g_max = self.get_min_max()
        return [(g_min[0] + g_max[0]) / 2, (g_min[1] + g_max[1]) / 2, g_min[2]]


# Contains 'GeometryInstance' (Template)
class GeometryInstance(CityGeometry):
    def __init__(self, geometry: GeometryPrimitive, matrix: TransformationMatrix):
        self.geometry = geometry
        self.matrix = matrix

    def transform(self, matrix: TransformationMatrix, center=None) -> None:
        """
        Apply the transformation matrix to the GeometryInstance's transformation matrix
        :param matrix: TransformationMatrix to apply to the geometry
        :param center: ignored (center is in self.matrix) - only used for compatibility with GeometryPrimitive
        """
        self.matrix = self.matrix.dot(matrix)

    def get_lod(self) -> str:
        """
        The LoD of the GeometryPrimitive is shared with all the GeometryInstances that use it
        :return: The level of detail of the geometry
        """
        return self.geometry.get_lod()

    def get_vertices(self, flatten=False) -> list:
        """
        Returns the vertices of the GeometryPrimitive after applying the transformation matrix of the GeometryInstance
        :param flatten: If True, the vertices are returned as a list of Vertex, else as the original structure of the geometry
        """
        vertices = self.geometry.get_vertices(flatten)
        return self.matrix.reproject_vertices(vertices)

    def duplicate(self) -> CityGeometry:
        """
        Keep the same reference to the geometry and create a new transformation matrix
        :return: A shallow copy of the geometry and a deep copy of the transformation matrix
        """
        return GeometryInstance(self.geometry, self.matrix.copy())

    def get_origin(self) -> Vertex:
        """
        :return: The origin of the geometry instance
        """
        return self.matrix.get_origin()

    def to_geometry_primitive(self) -> GeometryPrimitive:
        """
        Converts the GeometryInstance to a GeometryPrimitive
        Will apply the transformation matrix to the geometry primitive in the template
        :return: GeometryPrimitive
        """
        primitive = self.geometry.primitive.copy()
        primitive.transform(self.matrix)
        return GeometryPrimitive(primitive, self.geometry.lod)
