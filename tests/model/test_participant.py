import pytest

from secret_santa.model.participant import Participant


@pytest.fixture()
def participant_john() -> Participant:
    return Participant(full_name="John Doe", phone_number="+123456789")


@pytest.fixture()
def participant_john_nicknamed_johnny() -> Participant:
    # Same details as participant_john() but with a nickname
    return Participant(full_name="John Doe", phone_number="+123456789", nickname="Johnny")


@pytest.mark.parametrize(
    ("participant1", "participant2", "same"),
    [
        (pytest.lazy_fixture("participant_john"), pytest.lazy_fixture("participant_john"), True),
        (
            pytest.lazy_fixture("participant_john"),
            pytest.lazy_fixture("participant_john_nicknamed_johnny"),
            False,
        ),
    ],
)
def test_participant_eq(participant1: Participant, participant2: Participant, same: bool):
    assert (participant1 == participant2) == same, (
        f"Participant1: {participant1} and Participant2: {participant2} "
        f"should{' not' if not same else ''} be the equal."
    )
