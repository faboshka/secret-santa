import argparse
from argparse import Namespace
from typing import List

from .logging import LoggingUtils


class ArgParserUtils:
    """A class aggregating all the arguments' parser utilities needed."""

    class SmartFormatter(argparse.HelpFormatter):
        """A super class of argparse.HelpFormatter solemnly for allowing new lines in the ``argparser``'s help"""

        def _split_lines(self, text: str, width: int) -> List[str]:
            """
            Split lines and preserve line breaks in case ``text`` starts with ``|R`` (indicating raw).

            Args:
                text: The full string to be broken down according to the ``width`` given
                    and whether it starts with ``|R``.
                width: The width at which to wrap the text.

            Returns:
                A list of the broken down strings.

            """
            # If a line starts with R| (indicating Raw) preserve the line breaks and keep the indentation
            if text.startswith("R|"):
                import textwrap

                lines = []
                for line in text[2:].splitlines():
                    if line.strip():
                        lines.extend(textwrap.wrap(line, width))
                return lines
                # This is the RawTextHelpFormatter._split_lines
            return argparse.HelpFormatter._split_lines(self, text, width)

    @staticmethod
    def parse_args() -> Namespace:
        """
        Parse the program's arguments.

        Returns:
            The parsed arguments in a namespace.

        """
        # TODO: Improve the argument parser by adding more arguments
        parser = argparse.ArgumentParser(
            formatter_class=ArgParserUtils.SmartFormatter,
            description="Welcome to the Secret Santa Organizer, "
            "in which each participant gets one other participant assigned, "
            "to whom he should bring a gift!",
            epilog="Merry Christmas! and have lots of fun :)",
        )
        parser.add_argument(
            "--env-path",
            default=None,
            help="R|path to the .env file containing the required secrets\n"
            'If omitted - will try to load the "{project_root}/.env".\n'
            "--> Note: No error will be raised in case --env-path is not provided "
            'and no "{project_root}/.env" exists.',
        )
        parser.add_argument(
            "--participants-path",
            default=None,
            help='R|path to the "Secret Santa" participants JSON\n'
            'If omitted - will try to load "{project_root}/participants.json".',
        )
        # TODO: Create a new logging level with the highest value possible and log the players arrangement
        parser.add_argument(
            "--show-arrangement",
            default=False,
            action="store_true",
            help="R|show the final arrangement (participant -> receiver)\n"
            "--> Note: The --show-arrangement is shown as logged INFO, which means "
            "setting the logger any higher will not show the arrangements as expected.\n"
            "--> Personal Request: Please keep it fun and use this only for development-testing purposes / "
            "if you're a non-participating admin.",
        )
        parser.add_argument(
            "--dry-run",
            default=False,
            action="store_true",
            help="run the program without actually sending the message",
        )
        parser.add_argument(
            "-log",
            "--logging-level",
            default="info",
            type=str.lower,
            choices=LoggingUtils.logging_levels,
            help='set the main logging level of the program loggers (Defaults to "info")',
        )
        return parser.parse_args()
