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

    def dot(self, matrix) -> 'TransformationMatrix':
        new_matrix = np.dot(self.get_np_matrix(), matrix.get_np_matrix())
        new_matrix = round_matrix(numpy_to_list(new_matrix))
        return TransformationMatrix(new_matrix)

    def move(self, x, y, z) -> 'TransformationMatrix':
        new_matrix = self.get_np_matrix()
        new_matrix[0][3] += x
        new_matrix[1][3] += y
        new_matrix[2][3] += z
        return TransformationMatrix(numpy_to_list(new_matrix))

    def scale(self, x, y, z) -> 'TransformationMatrix':
        new_matrix = self.get_np_matrix()
        new_matrix[0][0] *= x
        new_matrix[1][1] *= y
        new_matrix[2][2] *= z
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

    def to_cj(self):
        return self.matrix

