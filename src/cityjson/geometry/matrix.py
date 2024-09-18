import numpy as np


def identity_matrix():
    return [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]


def rotate_x(angle_degree):
    angle = np.radians(angle_degree)
    matrix = identity_matrix()
    matrix[5] = np.cos(angle)
    matrix[6] = np.sin(angle)
    matrix[9] = -np.sin(angle)
    matrix[10] = np.cos(angle)
    return matrix


def rotate_y(angle_degree):
    angle = np.radians(angle_degree)
    matrix = identity_matrix()
    matrix[0] = np.cos(angle)
    matrix[2] = -np.sin(angle)
    matrix[8] = np.sin(angle)
    matrix[10] = np.cos(angle)
    return matrix


def rotate_z(angle_degree):
    angle = np.radians(angle_degree)
    matrix = identity_matrix()
    matrix[0] = np.cos(angle)
    matrix[1] = np.sin(angle)
    matrix[4] = -np.sin(angle)
    matrix[5] = np.cos(angle)
    return matrix


def round_matrix(matrix_list):
    return [round(val, 16) for val in matrix_list]


def list_to_numpy(matrix_list):
    return np.array(matrix_list).reshape(4, 4).astype(float)


def numpy_to_list(matrix_numpy):
    return matrix_numpy.flatten().tolist()


class TransformationMatrix:
    # matrix is a 4x4 matrix in a list of shape 1x16
    def __init__(self, matrix=None):
        self.matrix: list = identity_matrix() if matrix is None else round_matrix(matrix)

    def __str__(self):
        return str(self.get_np_matrix().tolist())

    def copy(self) -> 'TransformationMatrix':
        return TransformationMatrix(self.matrix.copy())

    def get_matrix(self):
        return self.matrix.copy()

    def get_np_matrix(self):
        return list_to_numpy(self.matrix)

    def get_origin(self):
        return [self.matrix[3], self.matrix[7], self.matrix[11]]

    def recenter(self) -> 'TransformationMatrix':
        origin = self.get_origin()
        return self.translate([-origin[0], -origin[1], -origin[2]])

    # the order is reversed to apply the transformations to the self.matrix
    def dot(self, matrix, from_origin=False) -> 'TransformationMatrix':
        origin = [0, 0, 0] if from_origin else self.get_origin()
        new_matrix = self.copy() if from_origin else self.recenter()
        new_matrix = np.dot(matrix.get_np_matrix(), new_matrix.get_np_matrix())
        new_matrix = round_matrix(numpy_to_list(new_matrix))
        return TransformationMatrix(new_matrix).translate(origin)

    def translate(self, vector) -> 'TransformationMatrix':
        new_matrix = self.get_np_matrix()
        new_matrix[0][3] += vector[0]
        new_matrix[1][3] += vector[1]
        new_matrix[2][3] += vector[2]
        return TransformationMatrix(numpy_to_list(new_matrix))

    def scale(self, vector) -> 'TransformationMatrix':
        new_matrix = self.get_np_matrix()
        new_matrix[0][0] *= vector[0]
        new_matrix[1][1] *= vector[1]
        new_matrix[2][2] *= vector[2]
        return TransformationMatrix(numpy_to_list(new_matrix))

    def __rotate(self, angle_degree, from_origin, rotate_function) -> 'TransformationMatrix':
        rot_matrix = TransformationMatrix(rotate_function(angle_degree))
        return self.dot(rot_matrix, from_origin)

    def rotate_x(self, angle_degree, from_origin=False) -> 'TransformationMatrix':
        return self.__rotate(angle_degree, from_origin, rotate_x)

    def rotate_y(self, angle_degree, from_origin=False) -> 'TransformationMatrix':
        return self.__rotate(angle_degree, from_origin, rotate_y)

    def rotate_z(self, angle_degree, from_origin=False) -> 'TransformationMatrix':
        return self.__rotate(angle_degree, from_origin, rotate_z)

    def __reproject(self, vertices):
        result = []
        for item in vertices:
            if isinstance(item[0], list):
                result.append(self.__reproject(item))
            else:
                result.append(self.reproject_vertice(item))
        return result

    def reproject_vertices(self, vertices):
        return self.__reproject(vertices)

    def reproject_vertice(self, vertice):
        matrix = self.get_np_matrix()
        vertice = np.array([vertice[0], vertice[1], vertice[2], 1])
        vertice = np.dot(matrix, vertice)
        vertice = vertice[:-1]
        return vertice.tolist()

    # todo refactor or rename
    def to_cj(self):
        matrix = self.matrix
        for i in range(16):
            int_val = int(matrix[i])
            flt_val = matrix[i]
            matrix[i] = flt_val if int_val != flt_val else int_val
        return matrix

