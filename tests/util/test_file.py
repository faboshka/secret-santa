import os
from pathlib import Path

import pytest

from secret_santa.util import file


@pytest.fixture()
def test_file_path(tests_directory: Path) -> Path:
    return tests_directory / "data" / "simple_text.txt"


@pytest.fixture()
def tests_temp_directory(tests_directory: Path) -> Path:
    return tests_directory / "data" / "temp"


def test_read_file(test_file_path: Path) -> None:
    file_text = (
        f"This is a simple text file which will be used to test the read file function.\n"
        f"Let's hope it'll work :)"
    )
    read_file: str = file.read_file(file_name=test_file_path)
    assert read_file == file_text, "The file contents read does not match the expected content."


def test_create_file(tests_temp_directory: Path) -> None:
    new_file_path: Path = tests_temp_directory / "simple_create_file.txt"
    new_file_content: str = "This is a simple text file creation to test create_file()"
    try:
        file.create_file(full_file_name=new_file_path, content=new_file_content)
        assert os.path.exists(
            new_file_path
        ), f"A new txt file ({new_file_path}) should've been created"
        read_content: str = file.read_file(new_file_path)
        assert (
            read_content == new_file_content
        ), f"The file {new_file_path} created did not contain the intended content."
    finally:
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
