"""File utilities."""

from os import PathLike


def create_file(full_file_name: PathLike, content: str) -> None:
    """Create a new file containing the ``content`` at the path specified ``full_file_name``.

    Args:
        full_file_name: Path (relative / absolute) to the file to be created.
        content: The content to write to the file.

    """
    with open(full_file_name, "w", encoding="utf8") as new_file:
        new_file.write(content)


def read_file(file_name: PathLike) -> str:
    """Read the contents of the file at ``file_name``.

    Args:
        file_name: Path (relative / absolute) to the file to be read.

    Returns:
        The contents of the file in one string in case ``read_line_by_line`` is False /
            as a list of strings read line by line in case ``read_line_by_line`` is True.

    """
    with open(file_name) as f:
        content = f.read()
    return content
