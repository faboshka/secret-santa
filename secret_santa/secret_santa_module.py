import copy
import json
import logging
import os
import random
import time
from os import PathLike
from pathlib import Path
from typing import Optional

import pyfiglet
from dotenv import load_dotenv

from secret_santa.twilio_messaging_service import TwilioMessagingService
from secret_santa.const import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from secret_santa.model.participant import Participant
from secret_santa.util import arg_parser, file, misc, path
from secret_santa.util import logging as logging_util

# Set up the main logger
logger = logging_util.get_logger("main")


class SecretSanta:
    """
    Secret Santa Class.

    Attributes:
        logger (logging.Logger): The class logger.
        participants (list[Participant]): A list of the Secret Santa participants.
        messaging_client (TwilioMessagingService): An instance of the messaging client.
        show_arrangement (bool): If ``True``, the relevant method will print the arrangement once it's calculated.
        dry_run (bool): If ``True``, the class methods will run a dry run (not execute some things,
            e.g. it won't actually send a message).

    """

    def __init__(
        self,
        participants_json_path: Optional[PathLike] = None,
        show_arrangement: bool = False,
        *,
        dry_run: bool,
    ) -> None:
        """
        Initialize the Secret Santa game class.

        Args:
            participants_json_path: Path to the "Secret Santa" participants JSON.
                If omitted, will try to look for the file at ``{project_root}/participants.json``.
            show_arrangement: Whether the arrangement will be shown once it's calculated.
            dry_run: If ``True``, the class methods will run a dry run (not execute some things).

        """
        # Set up the class logger
        self.logger = logging_util.get_logger(self.__class__.__name__)

        self.logger.debug("Initializing the Secret Santa class")

        # Load the participants
        if not participants_json_path:
            self.logger.warning("No path to the participants JSON has been passed")
            participants_json_path = path.get_project_root() / "participants.json"
            self.logger.debug("Attempting to look for a participants file at root level")
        assert Path(
            participants_json_path
        ).exists(), f"Could not find the participants JSON file @ {participants_json_path}"

        self.logger.debug("Loading the participants")
        self.participants = self.load_participants(participants_json_path=participants_json_path)
        self.logger.info(f"A total of {len(self.participants)} participants have been loaded")

        # Initialize the Twilio messaging client
        self.messaging_client = TwilioMessagingService(alphanumeric_id="SecretSanta")
        # Set whether the arrangement will be shown once it's decided
        self.show_arrangement = show_arrangement
        # Set whether the class methods should run a dry run or not
        self.dry_run = dry_run

        self.logger.info("SecretSanta class initialized")

    def load_participants(self, participants_json_path: PathLike) -> list[Participant]:
        """
        Read the JSON file at ``participants_json_path`` and load it into a list of participants.

        Args:
            participants_json_path: Path to the "Secret Santa" participants JSON.

        Returns:
            List of participants loaded from the file at ``participants_json_path``.

        """
        # Read the JSON file
        participants_json: str = file.read_file(Path(participants_json_path))
        # Convert the JSON string to a list of dicts
        participants_dict_list = json.loads(participants_json)
        assert len(participants_dict_list) > 2, (
            f"Secret Santa should have at least 3 participants. "
            f"Current number of participants: {len(participants_dict_list)}"
        )
        # Load the participants' dicts to a list of ``Participant``s
        participants = [Participant(**participant_dict) for participant_dict in participants_dict_list]
        for participant in participants:
            self.logger.debug(f"Loaded: {participant}")
        return participants

    def get_participants_derangement(self) -> list[Participant]:
        """
        Create and return a new list of the participants loaded to the class after a random derangement permutation,
        most likely to be used as the recipients.

        Returns:
            List of participants loaded to the class after a random derangement permutation.

        """
        # Create a new, deep copy of the participants loaded
        recipients = copy.deepcopy(self.participants)
        # Keep shuffling the copy until a derangement permutation of the participants is achieved
        # i.e. No two participants parallel to each other in the participants and the new list are the same
        while not misc.is_derangement(self.participants, recipients):
            random.shuffle(recipients)
        return recipients

    @staticmethod
    def get_participant_message_name(participant: Participant) -> str:
        """
        Get the name of the participant as it'll appear in the message to be sent.
        If the participant has a nickname, return it, otherwise, return the first part of their full name.

        Args:
            participant: The participant's details.

        Returns:
            The name of the participant as it'll appear in the message to be sent.

        """
        return participant.nickname if participant.nickname else participant.full_name.strip().split()[0]

    @staticmethod
    def get_secret_santa_message(participant: Participant, recipient: Participant) -> str:
        """
        Construct a message based on the participant and recipient's data.

        Args:
            participant: The participant's data, i.e. the gift giver.
            recipient: The recipient's data, i.e. the gift receiver.

        Returns:
            A customized message based on the participant and recipient's data.

        """
        # Participant name to use
        participant_msg_name = SecretSanta.get_participant_message_name(participant)
        # Recipient name to use
        recipient_msg_name = SecretSanta.get_participant_message_name(recipient)
        # Construct message
        message_body = f"Hello {participant_msg_name},\n" f"You'll be {recipient_msg_name}'s Secret Santa!"
        return message_body

    def run(self) -> int:
        """
        Find a recipient for each participant and send the participant a message using the messaging client initialized.

        Returns:
            0 in case everything runs successfully. Non-Zero code otherwise.

        """
        self.logger.info("Running the Secret Santa allocator")

        # Get a "Participant"s derangement to be used as the recipients
        participants_derangement = self.get_participants_derangement()
        # Go over the participants and recipients in the participants and participants_derangement lists respectively,
        # and send the participant a customized message
        for participant, recipient in zip(self.participants, participants_derangement):
            if self.show_arrangement:
                self.logger.info(
                    f"{SecretSanta.get_participant_message_name(participant)} -> "
                    f"{SecretSanta.get_participant_message_name(recipient)}"
                )
            response = self.messaging_client.send_message(
                SecretSanta.get_secret_santa_message(participant, recipient),
                participant.phone_number,
                dry_run=self.dry_run,
            )
            logger.info(f"Message sent to: {participant}, " f"Status: {response.status}")
        return 0


def load_env(dotenv_path: Optional[PathLike] = None, override_system: bool = False) -> None:
    """
    Check whether the environment has been configured correctly and the secrets needed has been passed.

    Args:
        dotenv_path: Custom path to the .env file. If omitted, will try to look for the ``{project_root}/.env`` file.
            (Defaults to None).
        override_system: Determine whether to override the system's environment variables if they're encountered in the
            files. (Defaults to False)

    """
    logger.debug("Loading the environment")
    # Read the .env file if exists and load it to the environment
    if not dotenv_path:
        logger.warning("No path to the .env file has been passed")
        root_dot_env = path.get_project_root() / ".env"
        logger.debug("Attempting to look for a .env file at root level")

        if root_dot_env.exists():
            logger.info(f"Reading .env file at: {dotenv_path}")
            dotenv_path = root_dot_env
        else:
            logger.warning(f"No .env file could be found at: {dotenv_path}")
            # load_dotenv won't fail in case the file does not exist and setting it to an empty
            # string would prevent it from looking for a `.env` file.
            dotenv_path = Path("")

    load_dotenv(dotenv_path=dotenv_path, override=override_system)

    # Make sure the needed Twilio configuration environment variables are provided
    logger.debug("Asserting Twilio configuration has been provided")
    required_env_vars = [TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER]
    if not all([os.getenv(env) for env in required_env_vars]):
        raise SystemExit(f"One or more of the environment variables needed ({required_env_vars}) has not been passed.")
    logger.info("Environment loaded successfully")


def main() -> int:
    """
    The module's main function.

    Returns:
        Zero in case the ``SecretSanta`` class is initialized and run as should be, non-Zero code otherwise.

    """
    secret_santa_figlet = pyfiglet.figlet_format("Secret  Santa")
    print(secret_santa_figlet)
    time.sleep(0.5)
    # Parse the provided arguments
    parser = arg_parser.get_secret_santa_argument_parser()
    args = parser.parse_args()
    # Get the root logger and update its level to set the main logging level
    logging.getLogger().setLevel(logging_util.logging_levels.get(args.logging_level, "info"))
    # Load the environment
    load_env(args.env_path)
    # Initialize the Secret Santa module and run it to send a message to the participants
    return SecretSanta(
        participants_json_path=args.participants_path,
        show_arrangement=args.show_arrangement,
        dry_run=args.dry_run,
    ).run()


if __name__ == "__main__":
    main()
