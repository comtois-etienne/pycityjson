import numpy as np

import pycityjson.model as cj
import pycityjson.io as cjio

from pycityjson.model.geometry import GeometryPrimitive
import math


file_path = "tests/test_files/railway.city.json"
city = cjio.read_cityjson(file_path)

print(city)
print(city.materials[0])
print(f'len materials: {len(city.materials)}')
print(f'len city.objects: {len(city.cityobjects)}')


# SolitaryVegetationObject with GeometryInstance
uuid = 'GMLID_SO0286258_965_2893'
cityobject = city[uuid]
print(cityobject)

geometry = cityobject.geometries[0]
print(f'is_geometry_primitive : {geometry.is_geometry_primitive()}')
print(f'number of surfaces: {geometry.surface_count()}')

matrix = cj.TransformationMatrix().translate((0, 0, 1.2)).rotate_y(90)
print(matrix)
cityobject.transform(matrix)

cjio.write_as_cityjson(city, '.tmp/test.city.json', pretty=True, purge_vertices=False)

