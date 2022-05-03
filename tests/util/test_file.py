import os
from pathlib import Path
from typing import List

import pytest

from secret_santa.util.file import FileUtils


@pytest.fixture()
def test_file_path(tests_directory: Path) -> Path:
    return tests_directory / "data" / "simple_text.txt"


@pytest.fixture()
def tests_temp_directory(tests_directory: Path) -> Path:
    return tests_directory / "data" / "temp"


@pytest.mark.parametrize("split_lines", [False, True])
def test_read_file(test_file_path: Path, split_lines: bool):
    file_text = (
        f"This is a simple text file which will be used to test the read file function.\n"
        f"Let's hope it'll work :)"
    )
    file_text_line_by_line = file_text.splitlines(keepends=True)
    read_file_lines: str | List[str] = FileUtils.read_file(
        file_name=test_file_path,
        read_line_by_line=split_lines,
    )
    assert read_file_lines == (
        file_text_line_by_line if split_lines else file_text
    ), "The file contents read does not match the expected content."


def test_create_file(tests_temp_directory: Path):
    new_file_path: Path = tests_temp_directory / "simple_create_file.txt"
    new_file_content: str = "This is a simple text file creation to test create_file()"
    try:
        FileUtils.create_file(full_file_name=new_file_path, content=new_file_content)
        assert os.path.exists(
            new_file_path
        ), f"A new txt file ({new_file_path}) should've been created"
        read_content: str = FileUtils.read_file(new_file_path)
        assert (
            read_content == new_file_content
        ), f"The file {new_file_path} created did not contain the intended content."
    finally:
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
