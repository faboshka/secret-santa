from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def tests_directory() -> Path:
    return Path(__file__).parent


@pytest.fixture(autouse=True)
def project_root_directory() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture(autouse=True)
def test_root_directory(request) -> Path:
    return Path(request.config.rootdir)
