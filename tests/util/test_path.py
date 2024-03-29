from pathlib import Path

from secret_santa.util import path


def test_get_project_root(project_root_directory: Path) -> None:
    # This more of a double validation, making sure that both point to the same directory
    code_project_root = path.get_project_root()
    assert code_project_root == project_root_directory, (
        f"The PathUtils.get_project_root() and project_root_directory do not point to the same directory as they "
        f"should: PathUtils.get_project_root(): {code_project_root}, project_root_directory: {project_root_directory}."
    )
