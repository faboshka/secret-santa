from argparse import ArgumentParser, Namespace
from copy import deepcopy
from typing import Sequence

import pytest

from secret_santa.util.arg_parser import ArgParserUtils


@pytest.fixture()
def secret_santa_arg_parser() -> ArgumentParser:
    return ArgParserUtils.get_secret_santa_argument_parser()


@pytest.fixture()
def default_namespace() -> Namespace:
    return Namespace(
        env_path=None,
        participants_path=None,
        show_arrangement=False,
        dry_run=False,
        logging_level="info",
    )


@pytest.mark.parametrize(
    ("input_", "namespace_diff"),
    [
        (["--dry-run"], Namespace(dry_run=True)),
        (
            ["--env-path", "dummy_env_path", "--participants-path", "dummy_participants_path"],
            Namespace(env_path="dummy_env_path", participants_path="dummy_participants_path"),
        ),
        (
            [
                "--logging-level",
                "critical",
                "--show-arrangement",
                "--dry-run",
                "--env-path",
                "dummy_env_path",
            ],
            Namespace(
                logging_level="critical",
                show_arrangement=True,
                dry_run=True,
                env_path="dummy_env_path",
            ),
        ),
        ("", pytest.lazy_fixture("default_namespace")),  # No arguments provided
    ],
)
def test_arg_parser(
    secret_santa_arg_parser: ArgumentParser,
    default_namespace: Namespace,
    input_: Sequence[str],
    namespace_diff: Namespace,
):
    def update_namespace_with_diff(namespace_: Namespace, namespace_diff_: Namespace) -> Namespace:
        updated_namespace = deepcopy(namespace_)
        for key, value in vars(namespace_diff_).items():
            setattr(updated_namespace, key, value)
        return updated_namespace

    resulting_namespace = update_namespace_with_diff(default_namespace, namespace_diff)
    namespace: Namespace = secret_santa_arg_parser.parse_args(input_)
    assert (
        namespace == resulting_namespace
    ), "The namespace constructed does not match the expected namespace."
