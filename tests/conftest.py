import json
import tempfile

import pytest


class FileManager:
    def save_json(self, content: dict) -> str:
        """
        Save the content into a JSON file and return the file path.
        """
        file_path = tempfile.mktemp()

        with open(file_path, 'w') as file:
            file.write(json.dumps(content))

        return file_path

    def get_empty_file_path(self) -> str:
        """
        TODO: comment
        """
        return tempfile.mktemp()


@pytest.fixture
def file_manager():
    """
    TODO: comment
    """
    return FileManager()
