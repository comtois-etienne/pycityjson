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


class TransformationMatrix:
    def __init__(self, matrix=None):
        self.matrix = identity_matrix() if matrix is None else matrix

    def get_matrix(self):
        return self.matrix
    
    def get_np_matrix(self):
        return np.array(self.matrix).reshape(4, 4)
    
    