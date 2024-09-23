from os import path

import pytest

@pytest.fixture
def get_file_path():
    """
    TODO: comment
    """
    file_folder = path.abspath(path.join(path.dirname(__file__), 'test_files'))

    def _get_file_path(file_name: str) -> str:
        return path.join(file_folder, file_name)

    return _get_file_path