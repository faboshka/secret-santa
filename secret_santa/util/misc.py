from typing import TypeVar

# A Generic type to be used as a generic type hint
T = TypeVar("T")  # Can be anything


class MiscUtils:
    """A class aggregating all the miscellaneous utilities needed (provided as static methods)."""

    @staticmethod
    def is_derangement(list_a: list[T], list_b: list[T]) -> bool:
        """
        Check whether ``list_b`` is a derangement permutation of ``list_a``.

        Note:
            This method does not check whether the two lists are a permutation of each other.

        Args:
            list_a: List of elements to check against ``list_b`` of the same type.
            list_b: List of elements to check against ``list_a`` of the same type.

        Returns:
            True in case each element in ``list_a`` is paralleled with a different element in ``list_b``.

        """
        # Assert both of the lists have at least one element
        assert len(list_a) > 0 and len(list_b) > 0, (
            f"The two lists must contain at least one element to qualify for a derangement check: "
            f"len(list_a)={len(list_a)}, len(list_b)={len(list_b)}"
        )
        # Assert the two lists are of the same length
        assert len(list_a) == len(list_b), (
            f"The two lists must be of the same size to qualify for a derangement check: "
            f"{len(list_a)} != {len(list_b)}"
        )
        # Assert the two lists contain items of the same type
        assert not any([True if type(x) != type(y) else False for x, y in zip(list_a, list_b)]), (
            f"The two lists' elements must be of the same type to qualify for a derangement check: "
            f"{type(list_a[0])} != {type(list_b[0])}"
        )

        # Each two parallel items should be different
        return all([True if x != y else False for x, y in zip(list_a, list_b)])
