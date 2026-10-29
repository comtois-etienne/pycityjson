"""High-level project and object helpers for CityJSON modeling."""

from enum import Enum

from pycityjson.guid import guid
from pycityjson.model import (
    City,
    CityObject,
    GeometryInstance,
    GeometryPrimitive,
    MultiPoint,
    Point,
    TransformationMatrix,
)


class CityObjectType(str, Enum):
    """Common CityJSON object types used by the modeling helpers."""

    BUILDING = 'Building'
    GROUND_SURFACE = 'GroundSurface'
    SOLITARY_VEGETATION_OBJECT = 'SolitaryVegetationObject'
    GENERIC_CITY_OBJECT = 'GenericCityObject'


class ModelingObject(CityObject):
    """A CityObject with an explicit project-space anchor point."""

    def __init__(self, cityobjects, type: str, anchor: list[float], uuid: str | None = None, project=None):
        """Create an object at ``anchor`` using an automatically generated UUID."""
        super().__init__(cityobjects, type, uuid=uuid or guid())
        self.anchor = list(anchor)
        self.project = project
        self._add_anchor_geometry()

    def _add_anchor_geometry(self) -> None:
        """Add the anchor point as a named ``origin`` geometry."""
        super().add_geometry(GeometryPrimitive(Point(*self.anchor), lod='origin'))

    def add_geometry(
        self,
        geometry: GeometryPrimitive,
        relative: bool = True,
        use_template: bool = False,
    ) -> None:
        """Add a geometry relative to the anchor, optionally as a template instance."""
        if relative:
            if use_template:
                if self.project is None:
                    raise ValueError('A template geometry requires a ModelingProject')
                template_index = self.project.geometry_templates.add_template(geometry)
                geometry = GeometryInstance(
                    geometry,
                    TransformationMatrix().translate(self.anchor),
                    template_index,
                )
            else:
                geometry = geometry.duplicate()
                geometry.transform(_translation(self.anchor), center=[0.0, 0.0, 0.0])
        super().add_geometry(geometry)

    def materialize_geometry(self, index: int) -> GeometryPrimitive:
        """Convert a template instance to an editable primitive geometry."""
        geometry = self.geometries[index]
        if isinstance(geometry, GeometryInstance):
            geometry = geometry.to_geometry_primitive()
            self.geometries[index] = geometry
        if not isinstance(geometry, GeometryPrimitive):
            raise TypeError('Only primitive or template-instance geometries can be materialized')
        return geometry

    def translate(self, vector: list[float]) -> None:
        """Translate the object and all of its geometries by ``vector``."""
        self.anchor = [a + v for a, v in zip(self.anchor, vector)]
        for geometry in self.geometries:
            geometry.transform(_translation(vector), center=[0.0, 0.0, 0.0])

    def translate_x(self, distance: float) -> None:
        """Translate the object along the X axis."""
        self.translate([distance, 0.0, 0.0])

    def translate_y(self, distance: float) -> None:
        """Translate the object along the Y axis."""
        self.translate([0.0, distance, 0.0])

    def translate_z(self, distance: float) -> None:
        """Translate the object along the Z axis."""
        self.translate([0.0, 0.0, distance])

    def rotate_x(self, angle: float) -> None:
        """Rotate all object geometry around its anchor on the X axis."""
        for geometry in self.geometries:
            geometry.transform(_rotation_x(angle), center=self.anchor)

    def rotate_y(self, angle: float) -> None:
        """Rotate all object geometry around its anchor on the Y axis."""
        for geometry in self.geometries:
            geometry.transform(_rotation_y(angle), center=self.anchor)

    def rotate_z(self, angle: float) -> None:
        """Rotate all object geometry around its anchor on the Z axis."""
        for geometry in self.geometries:
            geometry.transform(_rotation_z(angle), center=self.anchor)

    def scale(self, factor: list[float]) -> None:
        """Scale all object geometry around its anchor."""
        for geometry in self.geometries:
            geometry.transform(_scale(factor), center=self.anchor)


class ModelingProject(City):
    """A CityJSON project with convenient object and origin operations."""

    def __init__(self, origin: list[float] | None = None, epsg: int | None = None):
        """Create a project with an optional project origin and EPSG code."""
        super().__init__()
        self.project_origin = list(origin or [0.0, 0.0, 0.0])
        self.origin = self.project_origin.copy()
        if epsg is not None:
            self.set_epsg(epsg)

    def add_object(self, type: CityObjectType | str, anchor: list[float], uuid: str | None = None) -> ModelingObject:
        """Create and register a modeling object at an anchor coordinate."""
        object_type = type.value if isinstance(type, CityObjectType) else type
        object_ = ModelingObject(self.cityobjects, object_type, anchor, uuid, project=self)
        self.cityobjects.add_cityobject(object_)
        return object_

    def move_project(self, vector: list[float]) -> None:
        """Move the entire project, including its project origin, in space."""
        self.project_origin = [a + v for a, v in zip(self.project_origin, vector)]
        for object_ in self.cityobjects:
            if isinstance(object_, ModelingObject):
                object_.translate(vector)

    def move_project_x(self, distance: float) -> None:
        """Move the entire project along the X axis."""
        self.move_project([distance, 0.0, 0.0])

    def move_project_y(self, distance: float) -> None:
        """Move the entire project along the Y axis."""
        self.move_project([0.0, distance, 0.0])

    def move_project_z(self, distance: float) -> None:
        """Move the entire project along the Z axis."""
        self.move_project([0.0, 0.0, distance])

    def move_origin(self, origin: list[float]) -> None:
        """Change the project origin while keeping model coordinates in place."""
        self.project_origin = list(origin)
        self.origin = self.project_origin.copy()


def _translation(vector: list[float]):
    """Create a translation matrix."""
    from pycityjson.model import TransformationMatrix

    return TransformationMatrix().translate(vector)


def _rotation_x(angle: float):
    """Create an X-axis rotation matrix."""
    from pycityjson.model import TransformationMatrix

    return TransformationMatrix().rotate_x(angle)


def _rotation_y(angle: float):
    """Create a Y-axis rotation matrix."""
    from pycityjson.model import TransformationMatrix

    return TransformationMatrix().rotate_y(angle)


def _rotation_z(angle: float):
    """Create a Z-axis rotation matrix."""
    from pycityjson.model import TransformationMatrix

    return TransformationMatrix().rotate_z(angle)


def _scale(factor: list[float]):
    """Create an axis-scale matrix."""
    from pycityjson.model import TransformationMatrix

    return TransformationMatrix().scale(factor)
