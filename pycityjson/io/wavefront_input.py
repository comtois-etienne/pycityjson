from pathlib import Path

from pycityjson.guid import guid
from pycityjson.model import City, CityObject, Color, GeometryPrimitive, Material, MultiLineString, MultiPoint, MultiSurface, Point, Texture


def _parse_mtl(path: Path) -> tuple[dict[str, Material], dict[str, str]]:
    materials: dict[str, Material] = {}
    images: dict[str, str] = {}
    if not path.is_file():
        return materials, images

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
        elif current is not None and parts[0] == 'map_Kd' and len(parts) >= 2:
            images[current.name or ''] = ' '.join(parts[1:])
    return materials, images


def _vertex_index(value: str, count: int) -> int:
    index = int(value.split('/')[0])
    return index - 1 if index > 0 else count + index


def read_wavefront(
    file_path: str | Path,
    material_path: str | Path | None = None,
    lod: str | int = 0,
    type: str = 'GenericCityObject',
    add_uuid: bool = True,
    normalize: bool | tuple[bool, bool, bool] = False,
) -> City:
    """Read a Wavefront OBJ file into a CityJSON model."""
    path = Path(file_path)
    city = City()
    materials: dict[str, Material] = {}
    material_images: dict[str, str] = {}
    if material_path is not None:
        parsed_materials, parsed_images = _parse_mtl(Path(material_path))
        materials.update(parsed_materials)
        material_images.update(parsed_images)
    for material in materials.values():
        city.materials.add(material)

    vertices: list[list[float]] = []
    texture_vertices: list[list[float]] = []
    objects: dict[str, CityObject] = {}
    current_object: CityObject | None = None
    current_group: str | None = None
    current_material: Material | None = None
    group_faces: dict[
        tuple[str, str],
        list[tuple[list[int], list[int], Material | None]],
    ] = {}

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
            parsed_materials, parsed_images = _parse_mtl(material_file)
            materials.update(parsed_materials)
            material_images.update(parsed_images)
            for material in materials.values():
                city.materials.add(material)
        elif command == 'v' and len(parts) >= 4:
            vertices.append([float(value) for value in parts[1:4]])
        elif command == 'vt' and len(parts) >= 3:
            texture_vertices.append([float(parts[1]), float(parts[2])])
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
            vertex_indices = []
            texture_indices = []
            for value in parts[1:]:
                indices = value.split('/')
                vertex_indices.append(_vertex_index(value, len(vertices)))
                texture_index = indices[1] if len(indices) > 1 else ''
                texture_indices.append(
                    _vertex_index(texture_index, len(texture_vertices))
                    if texture_index
                    else -1,
                )
            group_faces.setdefault(key, []).append((
                vertex_indices,
                texture_indices,
                current_material,
            ))

    _normalize_vertices(vertices, normalize)
    city.vertices = city.vertices.__class__(vertices, precision=None)
    city.texture_vertices = texture_vertices
    for image in dict.fromkeys(material_images.values()):
        image_path = path.parent / image
        suffix = image_path.suffix.lower()
        texture_type = Texture.Type.PNG if suffix == '.png' else Texture.Type.JPG
        city.textures.append(Texture(texture_type, image))
    for (object_id, group), faces in group_faces.items():
        city_object = objects[object_id]
        surfaces = []
        texture_values: list[list[list[int]]] = []
        texture_theme: str | None = None
        for face, texture_indices, material in faces:
            points = [Point(*vertices[index]) for index in face]
            surface = MultiLineString([MultiPoint(points)])
            if material is not None:
                surface.set_material(material)
                if material.name in material_images:
                    texture_theme = material.name
                    texture_values.append([texture_indices])
            surfaces.append(surface)
        group_lod = group.removeprefix('lod_').removeprefix('lod').lstrip('_')
        group_lod = group_lod if group_lod.isdigit() else str(lod)
        geometry = GeometryPrimitive(MultiSurface(surfaces), group_lod)
        if texture_theme is not None:
            geometry.texture = {texture_theme: {'values': texture_values}}
        city_object.add_geometry(geometry)
    return city


def read_wavefront_geometries(
    file_path: str | Path,
    material_path: str | Path | None = None,
    lod: str | int = 0,
    normalize: bool | tuple[bool, bool, bool] = False,
) -> list[GeometryPrimitive]:
    """Read OBJ objects and groups as an ordered list of geometries."""
    city = read_wavefront(
        file_path,
        material_path=material_path,
        lod=lod,
        add_uuid=False,
        normalize=normalize,
    )
    geometries: list[GeometryPrimitive] = []
    for city_object in city.cityobjects:
        geometries.extend(
            geometry
            for geometry in city_object.geometries
            if isinstance(geometry, GeometryPrimitive)
        )
    return geometries


def _normalize_vertices(
    vertices: list[list[float]],
    normalize: bool | tuple[bool, bool, bool],
) -> None:
    """Normalize OBJ vertices in place according to the requested axes."""
    if normalize is False:
        return
    axes = (True, True, True) if normalize is True else normalize
    if len(axes) != 3:
        raise ValueError('normalize must be a bool or a three-item tuple')
    minimum = [min(vertex[axis] for vertex in vertices) for axis in range(3)]
    extent = [max(vertex[axis] for vertex in vertices) - minimum[axis] for axis in range(3)]
    scales = [1.0 / extent[axis] if axes[axis] and extent[axis] else 1.0 for axis in range(3)]
    selected_scales = [scales[axis] for axis in range(3) if axes[axis]]
    if not selected_scales:
        return
    fallback_scale = sum(selected_scales) / len(selected_scales)
    for axis in range(3):
        if not axes[axis]:
            scales[axis] = fallback_scale
        for vertex in vertices:
            vertex[axis] = (vertex[axis] - minimum[axis]) * scales[axis]


read_obj = read_wavefront
read_obj_geometries = read_wavefront_geometries
