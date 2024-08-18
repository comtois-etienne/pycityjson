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
    return list_to_numpy(matrix)


def rotate_y(angle_degree):
    angle = np.radians(angle_degree)
    matrix = identity_matrix()
    matrix[0] = np.cos(angle)
    matrix[2] = -np.sin(angle)
    matrix[8] = np.sin(angle)
    matrix[10] = np.cos(angle)
    return list_to_numpy(matrix)


def rotate_z(angle_degree):
    angle = np.radians(angle_degree)
    matrix = identity_matrix()
    matrix[0] = np.cos(angle)
    matrix[1] = np.sin(angle)
    matrix[4] = -np.sin(angle)
    matrix[5] = np.cos(angle)
    return list_to_numpy(matrix)


def round_matrix(matrix_list):
    return [round(val, 16) for val in matrix_list]


def list_to_numpy(matrix_list):
    return np.array(matrix_list).reshape(4, 4)


def numpy_to_list(matrix_numpy):
    return matrix_numpy.flatten().tolist()


class TransformationMatrix:
    # matrix is a 4x4 matrix of shape 1x16
    def __init__(self, matrix=None):
        self.matrix: list = identity_matrix() if matrix is None else round_matrix(matrix)

    def __str__(self):
        return str(self.matrix)

    def get_matrix(self):
        return self.matrix

    def get_np_matrix(self):
        return list_to_numpy(self.matrix)

    def get_origin(self):
        return [self.matrix[3], self.matrix[7], self.matrix[11]]

    def recenter(self) -> 'TransformationMatrix':
        origin = self.get_origin()
        return self.move([-origin[0], -origin[1], -origin[2]])

    def dot(self, matrix) -> 'TransformationMatrix':
        new_matrix = np.dot(self.get_np_matrix(), matrix.get_np_matrix())
        new_matrix = round_matrix(numpy_to_list(new_matrix))
        return TransformationMatrix(new_matrix)

    def move(self, vertice) -> 'TransformationMatrix':
        new_matrix = self.get_np_matrix()
        new_matrix[0][3] += vertice[0]
        new_matrix[1][3] += vertice[1]
        new_matrix[2][3] += vertice[2]
        return TransformationMatrix(numpy_to_list(new_matrix))

    def scale(self, vertice) -> 'TransformationMatrix':
        new_matrix = self.get_np_matrix()
        new_matrix[0][0] *= vertice[0]
        new_matrix[1][1] *= vertice[1]
        new_matrix[2][2] *= vertice[2]
        return TransformationMatrix(numpy_to_list(new_matrix))

    def rotate_x(self, angle_degree) -> 'TransformationMatrix':
        new_matrix = np.dot(self.get_np_matrix(), rotate_x(angle_degree))
        return TransformationMatrix(numpy_to_list(new_matrix))

    def rotate_y(self, angle_degree) -> 'TransformationMatrix':
        new_matrix = np.dot(self.get_np_matrix(), rotate_y(angle_degree))
        return TransformationMatrix(numpy_to_list(new_matrix))

    def rotate_z(self, angle_degree) -> 'TransformationMatrix':
        new_matrix = np.dot(self.get_np_matrix(), rotate_z(angle_degree))
        return TransformationMatrix(numpy_to_list(new_matrix))

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

    def to_cj(self):
        return self.matrix

