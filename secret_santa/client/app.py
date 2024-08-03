"""The secret santa app."""

import time
from pathlib import Path
from typing import Annotated, Optional

import pyfiglet
from typer import Option, Typer

from secret_santa.secret_santa_module import SecretSanta, load_env
from secret_santa.util import logging
from secret_santa.util.logging import LoggingLevel

secret_santa_app = Typer(
    short_help="Secret Santa client app.",
    help="Welcome to the Secret Santa Organizer, in which each participant gets one other participant assigned, "
    "to whom he should bring a gift!",
    no_args_is_help=True,
    rich_markup_mode="rich",
    epilog="Merry Christmas! and have lots of fun :)",
    add_completion=False,
)


@secret_santa_app.command(help="run the secret santa game", no_args_is_help=True)
def run(
    participants_path: Annotated[Path, Option(..., help="path to the 'Secret Santa' participants JSON")],
    env_path: Annotated[Optional[Path], Option(..., help="path to the 'Secret Santa' environment")] = None,
    show_arrangement: Annotated[
        bool,
        Option(
            ..., "--show-arrangement/--hide-arrangement", help="show the final arrangement (participant -> receiver)"
        ),
    ] = False,
    logging_level: Annotated[LoggingLevel, Option(..., case_sensitive=False, help="logging level")] = LoggingLevel.info,
    dry_run: Annotated[bool, Option(..., help="run the program without actually sending the message")] = False,
) -> int:
    """Run the secret santa game."""
    secret_santa_figlet = pyfiglet.figlet_format("Secret  Santa")
    print(secret_santa_figlet)  # noqa: T201
    time.sleep(0.5)
    logging.get_logger(add_common_handler=False).setLevel(str(logging_level).upper())
    load_env(env_path)
    return SecretSanta(
        participants_json_path=participants_path,
        show_arrangement=show_arrangement,
        dry_run=dry_run,
    ).run()


@secret_santa_app.command(help="run the secret santa game", no_args_is_help=True, hidden=True)
def validate() -> None:
    """Validate the secret santa game's participants."""


if __name__ == "__main__":
    secret_santa_app()
