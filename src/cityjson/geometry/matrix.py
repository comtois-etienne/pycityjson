import numpy as np
import math


def identity_matrix():
    return [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1
    ]

def rotate_x(angle):
    matrix = identity_matrix()
    matrix[5] = math.cos(angle)
    matrix[6] = math.sin(angle)
    matrix[9] = -math.sin(angle)
    matrix[10] = math.cos(angle)
    return matrix

def rotate_y(angle):
    matrix = identity_matrix()
    matrix[0] = math.cos(angle)
    matrix[2] = -math.sin(angle)
    matrix[8] = math.sin(angle)
    matrix[10] = math.cos(angle)
    return matrix

def rotate_z(angle):
    matrix = identity_matrix()
    matrix[0] = math.cos(angle)
    matrix[1] = math.sin(angle)
    matrix[4] = -math.sin(angle)
    matrix[5] = math.cos(angle)
    return matrix


def round_matrix(matrix):
    return [round(val, 16) for val in matrix]


class TransformationMatrix:
    def __init__(self, matrix=None):
        self.matrix = identity_matrix() if matrix is None else round_matrix(matrix)

    def __str__(self):
        return str(self.matrix)

    def get_matrix(self):
        return self.matrix

    def get_np_matrix(self):
        return np.array(self.matrix).reshape(4, 4)

    def dot(self, matrix) -> 'TransformationMatrix':
        new_matrix = np.dot(self.get_np_matrix(), matrix.get_np_matrix()).flatten().tolist()
        return TransformationMatrix(round_matrix(new_matrix))

