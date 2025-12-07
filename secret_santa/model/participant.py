"""Participant model."""

from attr import dataclass


@dataclass(frozen=True, kw_only=True)
class Participant:
    """A data class which holds the Secret Santa participants' information.

    Attributes:
        full_name: The participant's full name.
        phone_number: The participant's phone number.
        nickname: The participant's nickname which will be used.

    """

    full_name: str
    phone_number: str
    nickname: str | None = None
