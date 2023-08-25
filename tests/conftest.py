from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest


@pytest.fixture(autouse=True)
def tests_directory() -> Path:
    return Path(__file__).parent


@pytest.fixture(autouse=True)
def project_root_directory() -> Path:
    return Path(__file__).parent.parent


@pytest.fixture(autouse=True)
def test_root_directory(request: FixtureRequest) -> Path:
    return Path(request.config.rootdir)  # type: ignore[attr-defined]
