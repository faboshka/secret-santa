"""Twilio messaging service module."""

import os
import re
from typing import Optional

from attr import dataclass
from twilio.rest import Client

from secret_santa.const import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
from secret_santa.util import logging


@dataclass(kw_only=True)
class MessageResponse:
    """Custom message response class to hold the response of the send message call.

    Attributes:
        status: The status of the send message call.

    """

    status: str


class TwilioMessagingService:
    """Twilio Messaging Service Class.

    Attributes:
        logger: The class logger.
        twilio_number: The Twilio number the messages will be sent from.
        alphanumeric_id: An alphanumeric string which, if provided, will appear as the sender ID in the
            message to be sent.
            Warning: Please see the Twilio article on countries permitted to use the alphanumeric sender ID /
            whether pre-registration is needed.
        twilio_client: An instance of the twilio messaging client.

    """

    def __init__(self, alphanumeric_id: Optional[str] = None) -> None:
        """Initialize the Twilio messaging service.

        Args:
            alphanumeric_id: Alphanumeric sender ID which will be shown instead of the number.
                If omitted, the number provided in the environment will be shown as the sender ID. (Defaults to None).

                Warning: Please see the Twilio article on countries permitted to use the alphanumeric sender ID /
                whether pre-registration is needed.

        """
        # Set up the class logger
        self.logger = logging.get_logger(self.__class__.__name__)

        self.logger.debug("Initializing messaging client")

        # Load the Twilio service configuration / secrets
        (
            twilio_number,
            twilio_account_sid,
            twilio_auth_token,
        ) = self.load_twilio_config()
        self.twilio_number = twilio_number
        self.alphanumeric_id = alphanumeric_id

        # Check for alphanumeric sender ID and validate its correctness if exists
        if alphanumeric_id:
            # Assert at least one character exists
            assert bool(
                re.search("[a-zA-Z]", alphanumeric_id),
            ), "The alphanumeric sender Id needs to contain at least one character"
            # Assert the alphanumeric sender ID is up to Twilio's requirements
            assert bool(re.search(r"^[a-zA-Z0-9 ]{1,11}$", alphanumeric_id)), (
                "The alphanumeric sender Id can only contain up to 11 characters from the following categories:\n"
                "1) Upper-case letters A - Z\n"
                "2) Lower-case letters a - z\n"
                "3) Numbers 0 - 9\n"
                "4) Spaces\n"
            )

        # Initialize the Twilio client
        self.twilio_client = Client(username=twilio_account_sid, password=twilio_auth_token)

        self.logger.debug("Twilio client initialized")

    def load_twilio_config(self) -> tuple[str, str, str]:
        """Load the Twilio service configuration / secrets from the environment variables.

        This function asserts everything needed is present.

        Returns:
            The loaded ``TWILIO_NUMBER``, ``TWILIO_ACCOUNT_SID``, and ``TWILIO_AUTH_TOKEN`` in this specific order.

        """
        self.logger.debug("Loading Twilio configuration")
        # Load the environment variables needed
        twilio_account_sid = os.getenv(TWILIO_ACCOUNT_SID)
        twilio_auth_token = os.getenv(TWILIO_AUTH_TOKEN)
        twilio_number = os.getenv(TWILIO_NUMBER)

        # Assert the environment variables needed are present
        assert all([twilio_account_sid, twilio_auth_token, twilio_number]), (
            f"Required environment variables {TWILIO_ACCOUNT_SID} or {TWILIO_AUTH_TOKEN} "
            f"or {TWILIO_NUMBER} missing."
        )

        return twilio_number, twilio_account_sid, twilio_auth_token  # type: ignore

    def send_message(
        self,
        body: str,
        to: str,
        *,
        dry_run: bool,
    ) -> MessageResponse:
        """Send a text message with the string specified in the ``body`` to the number specified in ``to``.

        Args:
            body: The message to be sent to the number specified in the ``to`` parameter.
            to: The number of the recipient of the message specified in the ``body`` parameter.
            dry_run: If True, the invocation would be a dry run, i.e. the service won't actually send the message.

        Returns:
            A message response instance as a response of the message sent (or not sent in case of a dry run).
        """
        # Send the "body" message to the number specified in the "to" param
        # If an alphanumeric sender ID has been set, use it as the sender ID,
        # otherwise - Use the number provided in the environment
        if dry_run:
            # No need to actually send a message
            return MessageResponse(status="Not executed (DRY RUN)")
        response = self.twilio_client.messages.create(
            body=body,
            to=to,
            from_=self.alphanumeric_id if self.alphanumeric_id else self.twilio_number,
        )
        return MessageResponse(status=str(response.status))
