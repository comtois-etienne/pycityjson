from dataclasses import dataclass, field

import numpy as np

from .vertices import Vertex


@dataclass
class Vector:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def tolist(self) -> Vertex:
        return [self.x, self.y, self.z]


@dataclass(frozen=True)
class TransformationMatrix:
    """
    The transformation matrix is a 4x4 matrix used to apply transformations to vertices
    It is stored as a flat list of 16 elements
    The precision of the matrix is limited to 16 decimal places
    This class is immutable

    The init method takes a list of 16 elements or a 4x4 array and rounds the values to 16 decimal places
    """

    # The transformation matrix as a flat list of 16 elements (default identity matrix)
    __matrix: list[float | int] = field(default_factory=lambda: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])

    def __post_init__(self):
        """
        Flattens the matrix and rounds the values to 16 decimal places
        """
        matrix = np.array(self.__matrix).flatten().tolist()
        matrix = self.__round_matrix(matrix)
        object.__setattr__(
            self,
            '_TransformationMatrix__matrix',
            matrix,
        )

    def __str__(self) -> str:
        return str(self.get_np_matrix().tolist())

    def copy(self) -> 'TransformationMatrix':
        """
        :return: a deep copy of the transformation matrix
        """
        return TransformationMatrix(self.__matrix.copy())

    def tolist(self) -> list:
        """
        :return: a deep copy of the transformation matrix
        """
        return self.__matrix.copy()

    def get_np_matrix(self) -> np.ndarray:
        """
        :return: the transformation matrix as a numpy array of shape (4, 4)
        """
        return self.__list_to_numpy(self.__matrix)

    def get_origin(self) -> Vertex:
        """
        Index 3, 7, 11 are the origin of the transformation matrix used for translation
        :return: the origin of the transformation matrix
        """
        return [self.__matrix[3], self.__matrix[7], self.__matrix[11]]

    def recenter(self) -> 'TransformationMatrix':
        """
        Moves the origin of the transformation matrix to [0, 0, 0]
        :return: the recentered transformation
        """
        origin = self.get_origin()
        return self.translate([-origin[0], -origin[1], -origin[2]])

    def dot(self, matrix: 'TransformationMatrix', from_origin=False) -> 'TransformationMatrix':
        """
        Applies a dot product with another transformation matrix
        The order is reversed to apply the transformations to the self.matrix
        :param matrix: the transformation matrix to apply
        :param from_origin: if True the rotation is around the origin [0, 0, 0], otherwise it around the matrix's origin
        :return: the new transformation matrix
        """
        origin = [0, 0, 0] if from_origin else self.get_origin()
        new_matrix = self.copy() if from_origin else self.recenter()
        new_matrix = np.dot(matrix.get_np_matrix(), new_matrix.get_np_matrix())
        return TransformationMatrix(new_matrix).translate(origin)

    def translate(self, vector: Vertex | Vector) -> 'TransformationMatrix':
        """
        Applies a translation to the transformation matrix
        :param vector: the vector to translate the transformation matrix by
        :return: the translated transformation matrix
        """
        vector = self.__vector_to_vertex(vector)
        new_matrix = self.get_np_matrix()
        new_matrix[0][3] += vector[0]
        new_matrix[1][3] += vector[1]
        new_matrix[2][3] += vector[2]
        return TransformationMatrix(new_matrix)

    def scale(self, vector: Vertex | Vector) -> 'TransformationMatrix':
        """
        Scales the transformation matrix by a vector
        :param vector: the vector to scale the transformation matrix by
        :return: the scaled transformation matrix
        """
        vector = self.__vector_to_vertex(vector)
        new_matrix = self.get_np_matrix()
        new_matrix[0][0] *= vector[0]
        new_matrix[1][1] *= vector[1]
        new_matrix[2][2] *= vector[2]
        return TransformationMatrix(new_matrix)

    def __rotate(self, angle_degree: float, from_origin: bool, rotate_function) -> 'TransformationMatrix':
        """
        Applies a rotation to the transformation matrix
        :param angle_degree: the angle in degrees to rotate
        :param from_origin: if True the rotation is around the origin [0, 0, 0], otherwise it around the matrix's origin
        :param rotate_function: the function to create the rotation matrix
        """
        rot_matrix = TransformationMatrix(rotate_function(angle_degree))
        return self.dot(rot_matrix, from_origin)

    def rotate_x(self, angle_degree: float, from_origin=False) -> 'TransformationMatrix':
        """
        Applies a rotation around the x-axis to the transformation matrix
        :param angle_degree: the angle in degrees to rotate around the x-axis
        :param from_origin: if True the rotation is around the origin [0, 0, 0], otherwise it around the matrix's origin
        """
        return self.__rotate(angle_degree, from_origin, self.__rotate_x)

    def rotate_y(self, angle_degree: float, from_origin=False) -> 'TransformationMatrix':
        """
        Applies a rotation around the y-axis to the transformation matrix
        :param angle_degree: the angle in degrees to rotate around the y-axis
        :param from_origin: if True the rotation is around the origin [0, 0, 0], otherwise it around the matrix's origin
        """
        return self.__rotate(angle_degree, from_origin, self.__rotate_y)

    def rotate_z(self, angle_degree: float, from_origin=False) -> 'TransformationMatrix':
        """
        Applies a rotation around the z-axis to the transformation matrix
        :param angle_degree: the angle in degrees to rotate around the z-axis
        :param from_origin: if True the rotation is around the origin [0, 0, 0], otherwise it around the matrix's origin
        """
        return self.__rotate(angle_degree, from_origin, self.__rotate_z)

    def __reproject(self, vertices: list) -> list:
        """
        Used recursively to reproject a list of vertices or nested lists of vertices
        :param vertices: a list of vertices or nested lists of vertices
        :return: the reprojected list
        """
        result = []
        for item in vertices:
            # for nested lists
            if isinstance(item[0], list):
                result.append(self.__reproject(item))
            # for vertex
            else:
                result.append(self.reproject_vertex(item))
        return result

    def reproject_vertices(self, vertices: list) -> list:
        """
        Reprojects a list of vertices or nested lists of vertices
        Returns the list with the same nested structure
        :param vertices: a list of vertices or nested lists of vertices
        :return: the reprojected list
        """
        return self.__reproject(vertices)

    def reproject_vertex(self, vertex: Vertex | Vector) -> Vertex:
        """
        Reprojects a single vertex
        :param vertex: the vertex to reproject
        :return: the reprojected vertex
        """
        vertex = self.__vector_to_vertex(vertex)
        matrix = self.get_np_matrix()
        vertex = np.array([vertex[0], vertex[1], vertex[2], 1])
        vertex = np.dot(matrix, vertex)
        vertex = vertex[:-1]
        return vertex.tolist()

    @staticmethod
    def __vector_to_vertex(vector: Vertex | Vector) -> Vertex:
        """
        :param vector: the vector as a Vertex or Vector
        :return: the vector as a Vertex
        """
        return vector.tolist() if isinstance(vector, Vector) else vector

    @staticmethod
    def __list_to_numpy(matrix_list: list[float | int]) -> np.ndarray:
        """
        :param matrix_list: the transformation matrix as a flat list of 16 elements
        :return: the transformation matrix as a numpy array of shape (4, 4)
        """
        return np.array(matrix_list).reshape(4, 4).astype(float)

    @staticmethod
    def __round_matrix(matrix_list: list[float | int]) -> list[float | int]:
        """
        :param matrix_list: the transformation matrix as a flat list of 16 elements
        :return: the transformation matrix with a precision of 16 decimal places
        """
        return [round(val, 16) for val in matrix_list]

    @staticmethod
    def __rotate_x(angle_degree) -> list[float | int]:
        """
        :param angle_degree: the angle in degrees to rotate around the x-axis
        :return: the transformation matrix to rotate around the x-axis (shape 1x16)
        """
        angle = np.radians(angle_degree)
        matrix = TransformationMatrix().tolist()
        matrix[5] = np.cos(angle)
        matrix[6] = np.sin(angle)
        matrix[9] = -np.sin(angle)
        matrix[10] = np.cos(angle)
        return matrix

    @staticmethod
    def __rotate_y(angle_degree) -> list[float | int]:
        """
        :param angle_degree: the angle in degrees to rotate around the y-axis
        :return: the transformation matrix to rotate around the y-axis (shape 1x16)
        """
        angle = np.radians(angle_degree)
        matrix = TransformationMatrix().tolist()
        matrix[0] = np.cos(angle)
        matrix[2] = -np.sin(angle)
        matrix[8] = np.sin(angle)
        matrix[10] = np.cos(angle)
        return matrix

    @staticmethod
    def __rotate_z(angle_degree: float) -> list[float | int]:
        """
        :param angle_degree: the angle in degrees to rotate around the z-axis
        :return: the transformation matrix to rotate around the z-axis (shape 1x16)
        """
        angle = np.radians(angle_degree)
        matrix = TransformationMatrix().tolist()
        matrix[0] = np.cos(angle)
        matrix[1] = np.sin(angle)
        matrix[4] = -np.sin(angle)
        matrix[5] = np.cos(angle)
        return matrix
