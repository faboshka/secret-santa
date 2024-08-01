import itertools
import os
from argparse import Namespace
from pathlib import Path
from typing import Generator, Iterator

import pytest
from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch
from pytest_lazy_fixtures import lf
from pytest_mock import MockerFixture

import secret_santa.secret_santa_module
from secret_santa import __version__
from secret_santa.const import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from secret_santa.model.participant import Participant
from secret_santa.secret_santa_module import SecretSanta, load_env
from secret_santa.util import misc


# TODO: Remove in refactor and get rid of env load as this has some unintended side effects
@pytest.fixture(autouse=True)
def clear_environment(mocker: MockerFixture) -> Iterator:
    def is_github_environment_variable(name: str) -> bool:
        return any(name.startswith(gh_env_prefix) for gh_env_prefix in ["GITHUB_", "RUNNER_"])

    # This is essentially a pretest to clear the environment, as all tests run in the same session
    # with environment variables loaded from another tests.
    # Note:
    #   Until this is taken care of properly - the GitHub actions environment variables should not be cleared if exists.
    github_env_variables = {key: val for key, val in os.environ.items() if is_github_environment_variable(key)}
    mocker.patch.dict(os.environ, {**github_env_variables}, clear=True)
    yield


@pytest.fixture()
def test_env_file_path(tests_directory: Path) -> Path:
    return tests_directory / "data" / "example.env"


@pytest.fixture()
def invalid_test_env_file(tests_directory: Path) -> Path:
    return tests_directory / "data" / "invalid_example.env"


@pytest.fixture()
def test_participants_file_path(tests_directory: Path) -> Path:
    return tests_directory / "data" / "participants_example.json"


@pytest.fixture()
def participant_john_jd_doe() -> Participant:
    return Participant(full_name="John Doe", phone_number="+1234567890", nickname="J.D.")


@pytest.fixture()
def participant_john_johnny_doe() -> Participant:
    return Participant(full_name="John Doe", phone_number="+1234567890", nickname="Johnny")


@pytest.fixture()
def participant_jane_doe() -> Participant:
    return Participant(full_name="Jane Doe", phone_number="+0987654321")


@pytest.fixture()
def participant_richard_rich_roe() -> Participant:
    return Participant(full_name="Richard Roe", phone_number="+1234509876", nickname="Rich")


@pytest.fixture()
def participant_howard() -> Participant:
    return Participant(full_name="Howard", phone_number="+1234509876")


@pytest.fixture()
def participants_in_participants_file(
    participant_john_johnny_doe: Participant,
    participant_jane_doe: Participant,
    participant_richard_rich_roe: Participant,
) -> list[Participant]:
    return [
        participant_john_johnny_doe,
        participant_jane_doe,
        participant_richard_rich_roe,
    ]


@pytest.fixture()
def default_secret_santa_instance(
    monkeypatch: MonkeyPatch,
    test_participants_file_path: Path,
) -> SecretSanta:
    monkeypatch.setenv(TWILIO_ACCOUNT_SID, "DummyTwilioAccountSIDValue")
    monkeypatch.setenv(TWILIO_AUTH_TOKEN, "DummyTwilioAuthToken")
    monkeypatch.setenv(TWILIO_NUMBER, "+1234567890")
    return SecretSanta(participants_json_path=test_participants_file_path, dry_run=False)


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_load_env_with_env_file(monkeypatch: MonkeyPatch, test_env_file_path: Path) -> None:
    load_env(test_env_file_path)
    assert (
        os.getenv(TWILIO_ACCOUNT_SID) == "DummyTwilioAccountSIDValue"
    ), f"The environment variable {TWILIO_ACCOUNT_SID} value loaded does not match the expected value."
    assert (
        os.getenv(TWILIO_AUTH_TOKEN) == "DummyTwilioAuthToken"
    ), f"The environment variable {TWILIO_AUTH_TOKEN} value loaded does not match the expected value."
    assert (
        os.getenv(TWILIO_NUMBER) == "+1234567890"
    ), f"The environment variable {TWILIO_NUMBER} value loaded does not match the expected value."
    monkeypatch.delenv(TWILIO_ACCOUNT_SID, raising=False)
    monkeypatch.delenv(TWILIO_AUTH_TOKEN, raising=False)
    monkeypatch.delenv(TWILIO_NUMBER, raising=False)


def test_load_invalid_env_file(invalid_test_env_file: Path) -> None:
    with pytest.raises(SystemExit) as exception_info:
        load_env(invalid_test_env_file)
    assert (
        "One or more of the environment variables needed "
        "(['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_NUMBER']) has not been passed."
        in str(exception_info.value)
    ), "The exception raised does not match the exception expected."


@pytest.mark.parametrize(
    ("override_system", "system_values", "expected"),
    [
        (
            True,
            [
                (TWILIO_ACCOUNT_SID, "DummyValue"),
                (TWILIO_AUTH_TOKEN, "DummyToken"),
                (TWILIO_NUMBER, "+0987654321"),
            ],
            [
                (TWILIO_ACCOUNT_SID, "DummyTwilioAccountSIDValue"),
                (TWILIO_AUTH_TOKEN, "DummyTwilioAuthToken"),
                (TWILIO_NUMBER, "+1234567890"),
            ],
        ),
        (
            False,
            [
                (TWILIO_ACCOUNT_SID, "DummyValue"),
                (TWILIO_AUTH_TOKEN, "DummyToken"),
                (TWILIO_NUMBER, "+0987654321"),
            ],
            [
                (TWILIO_ACCOUNT_SID, "DummyValue"),
                (TWILIO_AUTH_TOKEN, "DummyToken"),
                (TWILIO_NUMBER, "+0987654321"),
            ],
        ),
    ],
)
def test_env_file_value_override_existing(
    monkeypatch: MonkeyPatch,
    test_env_file_path: Path,
    override_system: bool,
    system_values: list[tuple[str, str]],
    expected: list[tuple[str, str]],
) -> None:
    for env_key, env_value in system_values:
        monkeypatch.setenv(env_key, env_value)
    load_env(dotenv_path=test_env_file_path, override_system=override_system)
    for expected_env_key, expected_env_value in expected:
        assert (
            os.getenv(expected_env_key) == expected_env_value
        ), f"The environment variable {expected_env_key} value loaded does not match the expected value."


def test_load_env_without_env_file_no_env(mocker: MockerFixture) -> None:
    mocker.patch.object(Path, "exists", return_value=False)
    with pytest.raises(SystemExit) as exception_info:
        load_env()
    assert (
        "One or more of the environment variables needed "
        "(['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_NUMBER']) has not been passed."
        in str(exception_info.value)
    ), "The exception raised does not match the exception expected."


def test_load_env_without_env_file_with_predefined_env(
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv(TWILIO_ACCOUNT_SID, "DummyTwilioAccountSIDValue")
    monkeypatch.setenv(TWILIO_AUTH_TOKEN, "DummyTwilioAuthToken")
    monkeypatch.setenv(TWILIO_NUMBER, "+1234567890")
    mocker.patch("os.path.exists", return_value=False)
    load_env()
    assert os.getenv(TWILIO_ACCOUNT_SID) == "DummyTwilioAccountSIDValue"
    assert os.getenv(TWILIO_AUTH_TOKEN) == "DummyTwilioAuthToken"
    assert os.getenv(TWILIO_NUMBER) == "+1234567890"


@pytest.mark.parametrize(
    ("dry_run", "show_arrangement"),
    itertools.product([False, True], [False, True]),
)
def test_module_main(
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    capsys: Generator[CaptureFixture[str], None, None],
    test_participants_file_path: Path,
    dry_run: bool,
    show_arrangement: bool,
) -> None:
    monkeypatch.setenv(TWILIO_ACCOUNT_SID, "DummyTwilioAccountSIDValue")
    monkeypatch.setenv(TWILIO_AUTH_TOKEN, "DummyTwilioAuthToken")
    monkeypatch.setenv(TWILIO_NUMBER, "+1234567890")
    create_message_mock = mocker.patch("twilio.rest.api.v2010.account.message.MessageList.create")

    mocker.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=Namespace(
            participants_path=test_participants_file_path,
            env_path="",
            logging_level="info",
            dry_run=dry_run,
            show_arrangement=show_arrangement,
        ),
    )
    # TODO: Capture the output and check the "->" of the show arrangement appears in the log
    #  in case it is True / if "Dry run" appears in the log in case it is a dry run.
    assert (
        secret_santa.secret_santa_module.main() == 0
    ), "The module main did not return a zero exit status as expected."
    if dry_run:
        create_message_mock.assert_not_called()
    else:
        assert (
            create_message_mock.call_count == 3
        ), "The `create` method of the Twilio API was not called the number of times expected 3."


@pytest.mark.parametrize(
    ("dry_run", "show_arrangement"),
    itertools.product([False, True], [False, True]),
)
def test_init(
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    test_participants_file_path: Path,
    dry_run: bool,
    show_arrangement: bool,
) -> None:
    monkeypatch.setenv(TWILIO_ACCOUNT_SID, "DummyTwilioAccountSIDValue")
    monkeypatch.setenv(TWILIO_AUTH_TOKEN, "DummyTwilioAuthToken")
    monkeypatch.setenv(TWILIO_NUMBER, "+1234567890")
    mocker.patch(
        "secret_santa.secret_santa_module.SecretSanta.load_participants",
        return_value=mocker.MagicMock(),
    )

    secret_santa_obj = SecretSanta(
        participants_json_path=test_participants_file_path,
        show_arrangement=show_arrangement,
        dry_run=dry_run,
    )

    assert secret_santa_obj.logger.name == "SecretSanta", "The logger was not initialized with the proper name."
    assert (
        secret_santa_obj.dry_run == dry_run
    ), 'The value initialized in the object for "dry_run" does not match the expected value.'
    assert secret_santa_obj.show_arrangement == show_arrangement, (
        'The value initialized in the object for "show_arrangement" does not match the ' "expected value."
    )
    assert secret_santa_obj.messaging_client is not None, "The messaging service was not initialized as expected."


def test_init_defaults(
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    project_root_directory: Path,
) -> None:
    monkeypatch.setenv(TWILIO_ACCOUNT_SID, "DummyTwilioAccountSIDValue")
    monkeypatch.setenv(TWILIO_AUTH_TOKEN, "DummyTwilioAuthToken")
    monkeypatch.setenv(TWILIO_NUMBER, "+1234567890")
    path_join_mock = mocker.patch.object(
        Path,
        "__truediv__",
        return_value=project_root_directory / "participants.json",
    )
    mocker.patch.object(Path, "exists", return_value=True)
    load_participants_mock = mocker.patch(
        "secret_santa.secret_santa_module.SecretSanta.load_participants",
        return_value=mocker.MagicMock(),
    )

    secret_santa_obj = SecretSanta(dry_run=True)

    path_join_mock.assert_called()
    load_participants_mock.assert_called_once_with(participants_json_path=project_root_directory / "participants.json")
    assert (
        secret_santa_obj.show_arrangement is False
    ), "The default value for show_arrangement does not match the expected value."


def test_load_participants(
    default_secret_santa_instance: SecretSanta,
    test_participants_file_path: Path,
    participants_in_participants_file: list[Participant],
) -> None:
    loaded_participants = default_secret_santa_instance.load_participants(test_participants_file_path)

    assert (
        loaded_participants == participants_in_participants_file
    ), "The list of participants loaded does not match the expected list of participants."


@pytest.mark.parametrize(
    ("participant", "expected_message_name"),
    [
        (lf("participant_john_jd_doe"), "J.D."),
        (lf("participant_jane_doe"), "Jane"),
        (lf("participant_richard_rich_roe"), "Rich"),
        (lf("participant_howard"), "Howard"),
    ],
)
def test_get_participant_message_name(
    default_secret_santa_instance: SecretSanta,
    participant: Participant,
    expected_message_name: str,
) -> None:
    message_name = default_secret_santa_instance.get_participant_message_name(participant)

    assert message_name == expected_message_name, "The message name returned does not match the expected message name."


@pytest.mark.parametrize("execution_number", range(9))
def test_participants_derangement(
    execution_number: int,
    default_secret_santa_instance: SecretSanta,
    participants_in_participants_file: list[Participant],
) -> None:
    participants_derangement = default_secret_santa_instance.get_participants_derangement()
    assert misc.is_derangement(
        default_secret_santa_instance.participants,
        participants_derangement,
    ), "The output of `get_participants_derangement` is not a derangement as expected."


@pytest.mark.parametrize(
    ("participant", "recipient", "expected_message"),
    [
        (
            lf("participant_john_jd_doe"),
            lf("participant_jane_doe"),
            "Hello J.D.,\nYou'll be Jane's Secret Santa!",
        ),
        (
            lf("participant_howard"),
            lf("participant_richard_rich_roe"),
            "Hello Howard,\nYou'll be Rich's Secret Santa!",
        ),
    ],
)
def test_secret_santa_message(
    default_secret_santa_instance: SecretSanta,
    participant: Participant,
    recipient: Participant,
    expected_message: str,
) -> None:
    message = default_secret_santa_instance.get_secret_santa_message(participant, recipient)
    assert message == expected_message, 'The "Secret Santa" message generated does not match the expected message.'


@pytest.mark.parametrize("dry_run", [False, True])
def test_run(
    mocker: MockerFixture,
    monkeypatch: MonkeyPatch,
    test_participants_file_path: Path,
    dry_run: bool,
) -> None:
    monkeypatch.setenv(TWILIO_ACCOUNT_SID, "DummyTwilioAccountSIDValue")
    monkeypatch.setenv(TWILIO_AUTH_TOKEN, "DummyTwilioAuthToken")
    monkeypatch.setenv(TWILIO_NUMBER, "+1234567890")
    create_message_mock = mocker.patch("twilio.rest.api.v2010.account.message.MessageList.create")

    secret_santa_obj = SecretSanta(
        participants_json_path=test_participants_file_path,
        dry_run=dry_run,
    )
    send_message_spy = mocker.spy(secret_santa_obj.messaging_client, "send_message")
    assert secret_santa_obj.run() == 0

    assert send_message_spy.call_count == len(secret_santa_obj.participants), (
        f"The class' `send_message` was not called the number of times expected "
        f"({len(secret_santa_obj.participants)})."
    )
    if dry_run:
        create_message_mock.assert_not_called()
    else:
        assert create_message_mock.call_count == len(secret_santa_obj.participants), (
            f"The `create` method of the Twilio API was not called the number of times expected "
            f"({len(secret_santa_obj.participants)})."
        )
