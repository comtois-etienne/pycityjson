import math
from .geometry import CityGeometry


"""
{
  "type": "SolitaryVegetationObject", 
  "geometry": [
    {
      "type": "GeometryInstance",
      "template": 0,
      "boundaries": [372],
      "transformationMatrix": [
        2.0, 0.0, 0.0, 0.0,
        0.0, 2.0, 0.0, 0.0,
        0.0, 0.0, 2.0, 0.0,
        0.0, 0.0, 0.0, 1.0
      ]
    }
  ]
}
"""

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

# Contains GeometryInstance (Template)
class GeometryInstance:
    def __init__(self, geometry: CityGeometry):
        self.origin = [0, 0, 0]
        self.geometry = geometry
        self.matrix = identity_matrix()

    def scale(self, x, y, z):
        self.matrix[0] = x
        self.matrix[5] = y
        self.matrix[10] = z

    def translate(self, x, y, z):
        self.origin[0] += x
        self.origin[1] += y
        self.origin[2] += z

    def rotate(self, x_angle=0, y_angle=0, z_angle=0):
        pass

    def set_origin(self, x, y, z):
        self.origin = [x, y, z]

    def set_matrix(self, matrix):
        self.matrix = matrix

    def to_cj(self, city) -> dict:
        vertices = city.get_vertices()
        boundary = vertices.add(self.origin)

        geometry_templates = city.get_geometry_templates()
        template_index = geometry_templates.add_template(self.geometry)
        
        cityinstance = {
            'type': 'GeometryInstance',
            'template': template_index,
            'boundaries': [boundary],
            'transformationMatrix': self.matrix
        }
        return cityinstance