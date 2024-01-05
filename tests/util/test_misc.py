import pytest

from secret_santa.util import misc
from secret_santa.util.misc import T


@pytest.mark.parametrize(
    ("list1", "list2", "is_derangement"),
    [
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [10, 9, 8, 7, 6, 5, 4, 3, 2, 1], True),
        ([1, 9, 5, 4, 6, 8, 3, 10, 2, 7], [5, 6, 9, 3, 7, 2, 10, 1, 4, 8], True),
        ([1, 9, 5, 4, 7, 8, 3, 10, 2, 6], [5, 6, 9, 3, 7, 2, 10, 1, 4, 8], False),
        (["str3", "str4", "str2", "str1", "str5"], ["str4", "str1", "str5", "str3", "str2"], True),
        (["str1", "str2", "str3", "str4", "str5"], ["str5", "str4", "str3", "str2", "str1"], False),
    ],
)
def test_is_derangement_valid_input(list1: list[T], list2: list[T], is_derangement: bool) -> None:
    assert misc.is_derangement(list1, list2) == is_derangement, (
        f"The second list permutation should{'' if is_derangement else ' not'} be a derangement of the first list, "
        f"but MiscUtils.is_derangement() shows otherwise."
    )


@pytest.mark.parametrize(
    ("list1", "list2"),
    [
        ([], []),
        ([1, 2, 3, 4, 5], []),
        ([], [1, 2, 3, 4, 5]),
    ],
)
def test_is_derangement_fails_on_empty_list(list1: list[T], list2: list[T]) -> None:
    with pytest.raises(AssertionError) as exception_info:
        misc.is_derangement(list1, list2)
    # fmt: off
    assert (
        "The two lists must contain at least one element to qualify for a derangement check"
        in str(exception_info.value)
    ), "The assertion raised does not match the assertion expected."  # fmt: on adds redundant parenthesis on this line
    # fmt: on


@pytest.mark.parametrize(
    ("list1", "list2"),
    [
        ([1, 2, 3, 4, 5], [4, 3, 2, 1]),
    ],
)
def test_is_derangement_fails_on_lists_of_different_length(list1: list[T], list2: list[T]) -> None:
    with pytest.raises(AssertionError) as exception_info:
        misc.is_derangement(list1, list2)
    assert "The two lists must be of the same size to qualify for a derangement check" in str(
        exception_info.value
    ), "The assertion raised does not match the assertion expected."


@pytest.mark.parametrize(
    ("list1", "list2"),
    [
        ([1, 2, 3, 4, 5], ["str5", "str4", "str3", "str2", "str1"]),
    ],
)
def test_is_derangement_fails_on_lists_of_different_types(list1: list[T], list2: list[T]) -> None:
    with pytest.raises(AssertionError) as exception_info:
        misc.is_derangement(list1, list2)
    assert "The two lists' elements must be of the same type to qualify for a derangement check" in str(
        exception_info.value
    ), "The assertion raised does not match the assertion expected."
