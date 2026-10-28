from pathlib import Path

from pycityjson.guid import guid
from pycityjson.model import City, CityObject, Color, GeometryPrimitive, Material, MultiLineString, MultiPoint, MultiSurface, Point


def _parse_mtl(path: Path) -> dict[str, Material]:
    materials: dict[str, Material] = {}
    if not path.is_file():
        return materials

    current: Material | None = None
    for raw_line in path.read_text().splitlines():
        parts = raw_line.split()
        if not parts:
            continue
        if parts[0] == 'newmtl' and len(parts) >= 2:
            current = Material(name=' '.join(parts[1:]))
            materials[current.name] = current
        elif current is not None and parts[0] in {'Ka', 'Kd', 'Ks'} and len(parts) >= 4:
            color = Color(*(float(value) for value in parts[1:4]))
            if parts[0] == 'Ka':
                current.ambientIntensity = sum(color.to_list()) / 3
            elif parts[0] == 'Kd':
                current.diffuseColor = color
            else:
                current.specularColor = color
    return materials


def _vertex_index(value: str, count: int) -> int:
    index = int(value.split('/')[0])
    return index - 1 if index > 0 else count + index


def read_wavefront(
    file_path: str | Path,
    material_path: str | Path | None = None,
    lod: str | int = 1,
    type: str = 'GenericCityObject',
    add_uuid: bool = True,
) -> City:
    """Read a Wavefront OBJ file into a CityJSON model."""
    path = Path(file_path)
    city = City()
    materials: dict[str, Material] = {}
    if material_path is not None:
        materials.update(_parse_mtl(Path(material_path)))
    for material in materials.values():
        city.materials.add(material)

    vertices: list[list[float]] = []
    objects: dict[str, CityObject] = {}
    current_object: CityObject | None = None
    current_group: str | None = None
    current_material: Material | None = None
    group_faces: dict[tuple[str, str], list[tuple[list[int], Material | None]]] = {}

    def ensure_object() -> CityObject:
        nonlocal current_object
        if current_object is None:
            object_uuid = guid() if add_uuid else 'obj-1'
            current_object = CityObject(city.cityobjects, type, uuid=object_uuid)
            city.cityobjects.add_cityobject(current_object)
            objects[current_object.uuid()] = current_object
        return current_object

    for raw_line in path.read_text().splitlines():
        parts = raw_line.split()
        if not parts or parts[0].startswith('#'):
            continue
        command = parts[0]
        if command == 'mtllib' and len(parts) >= 2:
            material_file = path.parent / ' '.join(parts[1:])
            materials.update(_parse_mtl(material_file))
            for material in materials.values():
                city.materials.add(material)
        elif command == 'v' and len(parts) >= 4:
            vertices.append([float(value) for value in parts[1:4]])
        elif command == 'o':
            name = ' '.join(parts[1:]).strip()
            tokens = name.split(maxsplit=1)
            uuid = tokens[0] if tokens else (guid() if add_uuid else f'obj-{len(objects) + 1}')
            object_type = tokens[1] if len(tokens) == 2 else type
            current_group = None
            current_object = objects.get(uuid)
            if current_object is None:
                current_object = CityObject(city.cityobjects, object_type, uuid=uuid)
                city.cityobjects.add_cityobject(current_object)
                objects[uuid] = current_object
        elif command == 'g':
            current_group = ' '.join(parts[1:]) or f'lod_{len(group_faces) + 1}'
            ensure_object()
        elif command == 'usemtl':
            current_material = materials.get(' '.join(parts[1:]))
        elif command == 'f' and len(parts) >= 4:
            object_id = ensure_object().uuid()
            group = current_group or '__default__'
            key = (object_id, group)
            group_faces.setdefault(key, []).append((
                [_vertex_index(value, len(vertices)) for value in parts[1:]],
                current_material,
            ))

    city.vertices = city.vertices.__class__(vertices, precision=None)
    for (object_id, group), faces in group_faces.items():
        city_object = objects[object_id]
        surfaces = []
        for face, material in faces:
            points = [Point(*vertices[index]) for index in face]
            surface = MultiLineString([MultiPoint(points)])
            if material is not None:
                surface.set_material(material)
            surfaces.append(surface)
        group_lod = group.removeprefix('lod_').removeprefix('lod').lstrip('_')
        group_lod = group_lod if group_lod.isdigit() else str(lod)
        city_object.add_geometry(GeometryPrimitive(MultiSurface(surfaces), group_lod))
    return city


def read_wavefront_geometries(
    file_path: str | Path,
    material_path: str | Path | None = None,
    lod: str | int = 2,
) -> list[GeometryPrimitive]:
    """Read OBJ objects and groups as an ordered list of geometries."""
    city = read_wavefront(
        file_path,
        material_path=material_path,
        lod=lod,
        add_uuid=False,
    )
    geometries: list[GeometryPrimitive] = []
    for city_object in city.cityobjects:
        geometries.extend(
            geometry
            for geometry in city_object.geometries
            if isinstance(geometry, GeometryPrimitive)
        )
    return geometries


read_obj = read_wavefront
read_obj_geometries = read_wavefront_geometries
