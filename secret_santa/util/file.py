from pathlib import Path
from typing import List


class FileUtils:
    """A class aggregating all the file utilities needed (provided as static methods)."""

    @staticmethod
    def create_file(full_file_name: str | Path, content: str) -> None:
        """
        Create a new file containing the ``content`` at the path specified ``full_file_name``.

        Args:
            full_file_name: Path (relative / absolute) to the file to be created.
            content: The content to write to the file.

        """
        with open(full_file_name, "w", encoding="utf8") as new_file:
            new_file.write(content)

    @staticmethod
    def read_file(file_name: str, read_line_by_line: bool = False) -> str | List[str]:
        """
        Read the contents of the file at ``file_name``.

        Args:
            file_name: Path (relative / absolute) to the file to be read.
            read_line_by_line: If True, the file's contents will be read line by line and a list will be returned,
                otherwise the file's contents will be read as one string to be returned to the user.

        Returns:
            The contents of the file in one string in case ``read_line_by_line`` is False /
                as a list of strings read line by line in case ``read_line_by_line`` is True.

        """
        with open(file_name) as f:
            content = f.readlines() if read_line_by_line else f.read()
        return content
