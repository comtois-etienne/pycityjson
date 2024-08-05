from .geometry.surface import CitySurface
from .geometry.volume import CityVolume

def replace(boundaries, vertices):
    result = []
    for b in boundaries:
        if isinstance(b, list):
            result.append(replace(b, vertices))
        else:
            result.append(vertices[b])
    return result

def flatten(nested_list):
    result = []
    for l in nested_list:
        if isinstance(l, list) and isinstance(l[0], list):
            result += flatten(l)
        else:
            result.append(l)
    return result


def parse_geometry(boundaries, surface_semantics, surface_values):
    volumes = []
    for volume in boundaries:
        for surface in volume:
            surfaces = []
            pass


#

class CitySolidGeometry:

    # todo remplacer par un parser - voir surface.py
    def __init__(self, data, vertices):
        self.vertices = vertices
        self.type = "Solid"
        self.lod = data.get('lod', '1')
        self.boundaries = data.get('boundaries', None)
        self.surfaces = data['semantics'].get('surfaces', None) if 'semantics' in data else None
        self.surfaces_values = data['semantics'].get('values', None) if 'semantics' in data else None

    def get_boundaries(self):
        return self.boundaries

    def get_vertices(self, flat=False):
        v = replace(self.boundaries, self.vertices)
        return flatten(v) if flat else v

    def to_dict(self):
        return {
            'type': self.type,
            'lod': self.lod,
            'boundaries': self.boundaries,
            'semantics': {
                'surfaces': self.surfaces,
                'values': self.surfaces_values
            }
        }

