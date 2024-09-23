import json
import tempfile

from pycityjson import io

class TestFoo:
    def test_foo(self, get_file_path):
        """
        Test that we can:
        - Load a city from a JSON file
        - Save it into a JSON file
        - The saved file is a valid JSON file

        """
        # Arrange
        uuid = 'GMLID_SO0286258_965_2893'
        file_path = get_file_path('railway.city.json')
        save_path = tempfile.mktemp(suffix='.json')
        # Act
        city = io.read(file_path)
        io.write_as_cityjson(city, save_path)

        # Assert
        json.load(open(save_path, 'r'))
