import pytest

from secret_santa.util import logging


@pytest.mark.parametrize("logger_name", [None, "SecretSanta", "TwilioMessagingService"])
def test_get_logger(logger_name: str) -> None:
    logger = logging.get_logger(name=logger_name)
    assert logger.name == ("root" if logger_name is None else logger_name), (
        "The name of the logger provided does not match the expected logger name."
    )
