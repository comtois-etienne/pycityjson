"""
"appearance": {
    "materials": [
        {
            "*** name": "roofandground",
            "ambientIntensity":  0.2000,
            "diffuseColor":  [0.9000, 0.1000, 0.7500],
            "emissiveColor": [0.9000, 0.1000, 0.7500],
            "specularColor": [0.9000, 0.1000, 0.7500],
            "shininess": 0.2,
            "transparency": 0.5,
            "isSmooth": false
        },
        {
            "*** name": "wall",
            "ambientIntensity":  0.4000,
            "diffuseColor":  [0.1000, 0.1000, 0.9000],
            "emissiveColor": [0.1000, 0.1000, 0.9000],
            "specularColor": [0.9000, 0.1000, 0.7500],
            "shininess": 0.0,
            "transparency": 0.5,
            "isSmooth": true
        }
    ],
    "textures": [
        {
            "*** type": "PNG",
            "*** image": "http://www.someurl.org/filename.jpg"
        },
        {
            "type": "JPG",
            "image": "appearances/myroof.jpg",
            "wrapMode": "wrap",
            "textureType": "unknown",
            "borderColor": [0.0, 0.1, 0.2, 1.0]
        }
    ]
    "vertices-texture": [],
    "default-theme-texture": "myDefaultTheme1",
    "default-theme-material": "myDefaultTheme2"
}


{
    "type": "Solid",
    "lod": "2.1",
    "boundaries": [
        [ [[0, 3, 2, 1]], [[4, 5, 6, 7]], [[0, 1, 5, 4]], [[1, 2, 6, 5]] ]
    ],
    "material": {
        "irradiation": {                # theme 1
            "values": [[0, 0, 1, null]]
        },
        "irradiation-2": {              # theme 2
            "values": [[2, 2, 1, null]]
        }
    }
}
"""

from dataclasses import dataclass

from pycityjson.guid import guid


@dataclass(frozen=True)  # immutable
class Color:
    """
    Can contain a color in RGB or RGBA format.
    Init with either 3 or 4 floats or 3 or 4 ints.
    """

    r: float
    g: float
    b: float
    a: float = None

    @staticmethod
    def f_to_i(f: float) -> int:
        """
        float to int
        :param f: float
        :return: int
        """
        return int(f * 255)

    @staticmethod
    def i_to_f(i: int) -> float:
        """
        int to float
        :param i: int
        :return: float
        """
        return i / 255

    def copy(self) -> 'Color':
        return Color(self.r, self.g, self.b, self.a)

    def get_type(self) -> str:
        """
        :return: 'int' if the color is in int format, 'float' if the color is in float format
        """
        if type(self.r) == int and type(self.g) == int and type(self.b) == int:
            return 'int'
        return 'float'

    def to_int(self) -> 'Color':
        """
        Convert the color to int format if it is in float format.
        :return: new Color
        """
        if self.get_type() == 'float':
            l = self.to_list()
            l = [Color.f_to_i(x) for x in l]
            return Color(*l)
        return self.copy()

    def to_float(self) -> 'Color':
        """
        Convert the color to float format if it is in int format.
        :return: new Color
        """
        if self.get_type() == 'int':
            l = self.to_list()
            l = [Color.i_to_f(x) for x in l]
            return Color(*l)
        return self.copy()

    def to_rgb(self) -> 'Color':
        """
        Removes the alpha channel if it exists.
        :return: new Color
        """
        return Color(self.r, self.g, self.b)

    def to_rgba(self, alpha: float = 1.0) -> 'Color':
        """
        Converts the color to RGBA format.
        Will convert the alpha to the same type as the color.
        :param alpha: float or int
        :return: new Color
        """
        if self.get_type() == 'int' and type(alpha) == float:
            alpha = Color.f_to_i(alpha)
        if self.get_type() == 'float' and type(alpha) == int:
            alpha = Color.i_to_f(alpha)
        return Color(self.r, self.g, self.b, alpha)

    def to_list(self) -> list:
        """
        Converts the color to a list.
        :return: list
        """
        l = [self.r, self.g, self.b]
        l.append(self.a) if self.a is not None else None
        return l


@dataclass()
class Material:
    name: str = None
    ambientIntensity: float = None
    diffuseColor: Color = None
    emissiveColor: Color = None
    specularColor: Color = None
    shininess: float = None
    transparency: float = None
    isSmooth: bool = None

    def __post_init__(self):
        if self.name is None:
            self.name = guid()
