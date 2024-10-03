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
    "vertices-texture": [
        [0.0, 0.5],
        [1.0, 0.0],
        [1.0, 1.0],
        [0.0, 1.0]
    ],
    "default-theme-texture": "myDefaultTheme1",
    "default-theme-material": "myDefaultTheme2"
}

"geometry": [
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
            },
            "irradiation-3": {              # theme 3
                "value": 2
            }
        }
    }
]
"""

from copy import copy
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
        return int(round(f * 255, 0))

    @staticmethod
    def i_to_f(i: int, round_decimals: int = None) -> float:
        """
        int to float
        :param i: int
        :return: float
        """
        v = i / 255
        v = round(v, round_decimals) if round_decimals is not None else v
        return v

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

    def to_float(self, round_decimals=3) -> 'Color':
        """
        Convert the color to float format if it is in int format.
        3 decimals are kept by default for 8bit colors.
        :return: new Color
        """
        if self.get_type() == 'int':
            l = self.to_list()
            l = [Color.i_to_f(x, round_decimals) for x in l]
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
    name: str = None  # mandatory
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

    def __eq__(self, other: 'Material') -> bool:
        return self.name == other.name


class Materials:
    """
    Container for materials.
    """

    def __init__(self):
        self.__materials: list[Material] = []
        self.__materials_dict: dict[str, int] = {}

    def __len__(self) -> int:
        """
        Returns the number of materials in the collection.
        """
        return len(self.__materials)

    def __getitem__(self, item: str | int) -> Material:
        """
        Returns the material at the given index or the material with the given name.
        :param item: str or int (name or index)
        :return: Material if item is an index or name, None if the item is not in the collection
        """
        if isinstance(item, int):
            return self.get_by_index(item)
        elif isinstance(item, str):
            return self.get_by_name(item)
        return None

    def __iter__(self):
        """
        Iterator for the materials.
        """
        return iter(self.__materials)

    def __contains__(self, item: Material) -> bool:
        """
        :param item: Material to check if it is in the collection
        :return: True if the material is in the collection, False otherwise
        """
        return item.name in self.__materials_dict

    def get_index(self, material: Material) -> int:
        """
        :param material: Material to get the index of
        :return: Index of the material in the collection. None if the material is not in the collection
        """
        if material not in self:
            return None
        return self.__materials_dict[material.name]

    def add(self, material: Material) -> int:
        """
        :param material: Material to add to the collection
        :return: Index of the added material in the collection
        """
        if material not in self:
            self.__materials_dict[material.name] = len(self.__materials)
            self.__materials.append(material)
        return self.get_index(material)

    def get_by_index(self, index: int) -> Material:
        """
        :param index: Index of the material to get
        :return: Material at the given index. None if the index is out of bounds
        """
        if index < 0 or index >= len(self.__materials):
            return None
        return self.__materials[index]

    def get_by_name(self, name: str) -> Material:
        """
        :param name: Name of the material to get
        :return: Material with the given name. None if the material is not in the collection
        """
        index = self.__materials_dict.get(name)
        if index is None:
            return None
        return self.__materials[index]

    def to_list(self) -> list:
        """
        :return: A copy of the list of materials in the collection
        """
        return copy(self.__materials)


@dataclass()
class Texture:
    class Type:
        PNG = 'PNG'
        JPG = 'JPG'

    class WrapMode:
        NONE = 'none'
        WRAP = 'wrap'
        MIRROR = 'mirror'
        CLAMP = 'clamp'
        BORDER = 'border'

    class TextureType:
        UNKNOWN = 'unknown'
        SPECIFIC = 'specific'
        TYPICAL = 'typical'

    type: str
    image_url: str
    wrap_mode: str = None
    texture_type: str = None
    border_color: Color = None  # RGBA
