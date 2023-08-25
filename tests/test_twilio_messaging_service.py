import itertools
from typing import Callable, Optional

import pytest
from _pytest.monkeypatch import MonkeyPatch
from pytest_lazyfixture import lazy_fixture
from pytest_mock import MockerFixture

from secret_santa.const import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from secret_santa.twilio_messaging_service import MessageResponse, TwilioMessagingService


@pytest.fixture()
def twilio_messaging_service_builder(
    monkeypatch: MonkeyPatch,
) -> Callable[[Optional[str]], TwilioMessagingService]:
    def _builder(alphanumeric_id: Optional[str] = None) -> TwilioMessagingService:
        monkeypatch.setenv(TWILIO_ACCOUNT_SID, "DummyValue1")
        monkeypatch.setenv(TWILIO_AUTH_TOKEN, "DummyValue2")
        monkeypatch.setenv(TWILIO_NUMBER, "DummyValue3")
        return TwilioMessagingService(alphanumeric_id=alphanumeric_id)

    return _builder


@pytest.fixture()
def twilio_messaging_service_alphanumeric_id_secret_santa(
    twilio_messaging_service_builder: Callable[[Optional[str]], TwilioMessagingService],
) -> TwilioMessagingService:
    return twilio_messaging_service_builder("SecretSanta")


@pytest.fixture()
def twilio_messaging_service(
    twilio_messaging_service_builder: Callable[[Optional[str]], TwilioMessagingService],
) -> TwilioMessagingService:
    return twilio_messaging_service_builder(None)


@pytest.mark.parametrize(
    "invalid_env_variable_key_value_tuple_list",
    [
        [
            (TWILIO_ACCOUNT_SID, "DummyValue"),
            (TWILIO_AUTH_TOKEN, "DummyValue"),
            (TWILIO_NUMBER, None),
        ],
        [
            (TWILIO_ACCOUNT_SID, "DummyValue"),
            (TWILIO_AUTH_TOKEN, None),
            (TWILIO_NUMBER, "DummyValue"),
        ],
        [
            (TWILIO_ACCOUNT_SID, None),
            (TWILIO_AUTH_TOKEN, None),
            (TWILIO_NUMBER, None),
        ],
    ],
)
def test_invalid_config(
    monkeypatch: MonkeyPatch,
    invalid_env_variable_key_value_tuple_list: list[tuple[str, str]],
) -> None:
    for env_key, env_value in invalid_env_variable_key_value_tuple_list:
        (
            monkeypatch.setenv(env_key, env_value)
            if env_value is not None
            else monkeypatch.delenv(env_key, raising=False)
        )
    with pytest.raises(AssertionError) as exception_info:
        TwilioMessagingService()
    assert (
        "Required environment variables TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN or TWILIO_NUMBER missing."
        in str(exception_info.value)
    ), "The assertion raised does not match the assertion expected."


def test_load_twilio_config(mocker: MockerFixture, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv(TWILIO_ACCOUNT_SID, "DummyValue1")
    monkeypatch.setenv(TWILIO_AUTH_TOKEN, "DummyValue2")
    monkeypatch.setenv(TWILIO_NUMBER, "DummyValue3")
    twilio_client_init_mock = mocker.patch("twilio.rest.Client.__init__", return_value=None)

    twilio_messaging_service = TwilioMessagingService()

    twilio_client_init_mock.assert_called_with(username="DummyValue1", password="DummyValue2")
    assert (
        twilio_messaging_service.twilio_number == "DummyValue3"
    ), f"The Twilio phone number (a.k.a. {TWILIO_NUMBER}) was not loaded in TwilioMessagingService as expected."


@pytest.mark.parametrize("alphanumeric_id", [None, "SecretSanta", "123123Drink", "Test Spaces"])
def test_twilio_messaging_service_alphanumeric_id(
    twilio_messaging_service_builder: Callable[[str | None], TwilioMessagingService],
    alphanumeric_id: str,
) -> None:
    twilio_messaging_service = twilio_messaging_service_builder(alphanumeric_id)
    assert twilio_messaging_service.alphanumeric_id == alphanumeric_id, (
        f"The alphanumeric ID loaded to the TwilioMessagingService instance "
        f"({twilio_messaging_service.alphanumeric_id}) does not match the expected alphanumeric ID ({alphanumeric_id})."
    )


@pytest.mark.parametrize("alphanumeric_id", ["Secret Santa", "123-Drink", "TestingSpaces"])
def test_invalid_twilio_messaging_service_alphanumeric_id(
    twilio_messaging_service_builder: Callable[[str | None], TwilioMessagingService],
    alphanumeric_id: str,
) -> None:
    with pytest.raises(AssertionError) as exception_info:
        twilio_messaging_service_builder(alphanumeric_id)
    assert (
        "The alphanumeric sender Id can only contain up to 11 characters from the following categories:"
        in str(exception_info.value)
    ), "The assertion raised does not match the assertion expected."


@pytest.mark.parametrize(
    ("twilio_messaging_service_", "dry_run"),
    itertools.product(
        [
            lazy_fixture("twilio_messaging_service"),
            lazy_fixture("twilio_messaging_service_alphanumeric_id_secret_santa"),
        ],
        [False, True],
    ),
)
def test_send_message(
    mocker: MockerFixture,
    twilio_messaging_service_: TwilioMessagingService,
    dry_run: bool,
) -> None:
    create_message_mock = mocker.patch("twilio.rest.api.v2010.account.message.MessageList.create")
    response = twilio_messaging_service_.send_message(
        body="Hello there :) This is the service send message test...",
        to="+0123456789",
        dry_run=dry_run,
    )

    if dry_run:
        assert response == MessageResponse(
            status="Not executed (DRY RUN)"
        ), "The response returned does not match the response expected."
    else:
        create_message_mock.assert_called_once_with(
            body="Hello there :) This is the service send message test...",
            to="+0123456789",
            from_=(
                twilio_messaging_service_.alphanumeric_id
                if twilio_messaging_service_.alphanumeric_id
                else twilio_messaging_service_.twilio_number
            ),
        )
