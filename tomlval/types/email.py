"""Email type for TOML values."""

import re
from typing import List, Optional

from tomlval.toml_error import TOMLError
from tomlval.toml_error_code import TOMLErrorCode
from tomlval.types.toml_type import TOMLType

email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class Email(TOMLType):
    """Represents an email address in a TOML schema."""

    def __init__(self, domains: Optional[List[str]] = None) -> None:
        """
        Initialize the Email type.

        Args:
            domains (List[str]): The expected domains of the email address.
        """
        self.domains = domains

    def __str__(self) -> str:
        if self.domains:
            domains = ", ".join([f"'{domain}'" for domain in self.domains])
            return f"<Email domains='{domains}'>"
        return "<Email>"

    def __repr__(self) -> str:
        return str(self)

    def validate(self, value: str) -> Optional[TOMLError]:
        if not isinstance(value, str):
            return TOMLError(TOMLErrorCode.INVALID_TYPE)
        if not email_pattern.match(value):
            return TOMLError(TOMLErrorCode.INVALID_EMAIL)
        if self.domains:
            domain = value.split("@")[-1]
            if domain not in self.domains:
                return TOMLError(TOMLErrorCode.INVALID_DOMAIN)

        return None
