from attr import dataclass


@dataclass(eq=False, frozen=True)
class Participant:
    """
    A data class which holds the Secret Santa participants' information.

    Attributes:
        full_name: The participant's full name.
        phone_number: The participant's phone number.
        nickname: The participant's nickname which will be used.

    """

    full_name: str
    phone_number: str
    nickname: str | None = None

    # TODO: Replace `ignore` with Self from typing once Python 3.11 is supported (and the type checker supports it).
    def __eq__(self, other) -> bool:  # type: ignore
        """
        Custom equals method for this data class to check if two participants are identical.

        Args:
            other: The other participant to check against ``self``.

        Returns:
            True if all the properties of ``self`` and ``other`` match, False otherwise.

        """
        if not isinstance(other, Participant):
            return NotImplemented
        return (
            self.full_name == other.full_name
            and self.phone_number == other.phone_number
            and self.nickname == other.nickname
        )
