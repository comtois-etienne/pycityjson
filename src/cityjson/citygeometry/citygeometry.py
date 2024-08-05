from .geometrytype.primitive import CitySolidGeometry


class CityGeometry:
    def __init__(self, data, cityjson):
        self._data = data # use self._geometry
        self.cityjson = cityjson
        self._init_geometries()
    
    #todo
    def _init_geometries(self):
        if not hasattr(self, '_geometries'):
            self._geometries = []
            for geometry in self._data:
                if geometry['type'] == 'Solid':
                    self._geometries.append(CitySolidGeometry(geometry, self.cityjson.get_vertices()))
                else:
                    print("Geometry type not implemented yet")
    
    def get_boundaries(self):
        boundaries = []
        for geometry in self._geometries:
            boundaries.append(geometry.get_boundaries())
        return boundaries
    
    def get_vertices(self, flat=False):
        v = [geometry.get_vertices(flat) for geometry in self._geometries]
        return v[0] if flat else v
    
    def get_max(self, axis=0):
        v = self.get_vertices(flat=True)
        return max([coord[axis] for coord in v])
    
    def get_min(self, axis=0):
        v = self.get_vertices(flat=True)
        return min([coord[axis] for coord in v])
    
    def to_dict(self):
        return [geometry.to_dict() for geometry in self._geometries]

