# PyCityJSON
Python CityJSON io, editor and modeling library

Loading a file :  
```py
import pycityjson.io as cjio
import pycityjson.model as cj

city = cjio.read('railway.city.json')
```

Selecting an object :  
```py
# SolitaryVegetationObject with GeometryInstance
uuid = 'GMLID_SO0286258_965_2893'
cityobject = city[uuid]
```

Applying a transformation on an object :  
```py
matrix = cj.TransformationMatrix().translate((0, 0, 12))
cityobject.transform(matrix)
```

Saving the modified CityJSON file :  
```py
cjio.write_as_cityjson(city, 'railway_modified.city.json', pretty=False, purge_vertices=True)
```

Saving the modified CityJSON to wavefront :  
```py
cjio.write_as_wavefront(city, 'railway_modified.obj', as_one_geometry=False, swap_yz=True)
```

# Specifications
https://www.cityjson.org/specs/2.0.1/

# Dataset
https://www.cityjson.org/datasets/

# Ruff
- lint `ruff check --fix .`
- format `ruff format .`

# TODO / WIP  
- Materials export  
- Textures (input & output)
- Extensions  
