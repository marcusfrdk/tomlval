"""Email type used in the TOML schema."""

import re
from typing import List, Optional

from tomlval.errors.error_code import ErrorCode
from tomlval.types._toml_error import TOMLError
from tomlval.types._toml_type import TOMLType
from tomlval.utils import quote_list

NOT_A_LIST_MESSAGE = "Domains must be a list."
INVALID_TYPES_MESSAGE = "Invalid type(s): %s"
INVALID_DOMAINS_MESSAGE = "Invalid domain(s): %s"

email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
domain_pattern = re.compile(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class Email(TOMLType):
    """Represents an email address in a TOML schema."""

    def __init__(self, domains: Optional[List[str]] = None) -> None:
        """
        Initialize the Email type.

        Args:
            domains (List[str]): The expected domains of the email address.

        Raises:
            TypeError: If domains is not a list of strings.
            ValueError: If any domain is not a valid domain name.
        """
        if domains is None:
            domains = []

        if not isinstance(domains, list):
            raise TypeError(NOT_A_LIST_MESSAGE)

        if invalid_values := [
            domain for domain in domains if not isinstance(domain, str)
        ]:
            _types = ", ".join([type(v).__name__ for v in invalid_values])
            raise TypeError(INVALID_TYPES_MESSAGE % _types)

        if invalid_domains := [
            domain for domain in domains if not domain_pattern.match(domain)
        ]:
            _domains = ", ".join(quote_list(invalid_domains))
            raise ValueError(INVALID_DOMAINS_MESSAGE % _domains)

        self.domains = domains

    def __str__(self) -> str:
        if self.domains:
            domains = ", ".join([f"'{domain}'" for domain in self.domains])
            return f"<Email domains='{domains}'>"
        return "<Email>"

    def __repr__(self) -> str:
        return str(self)

    def validate(self, value: str):
        if not isinstance(value, str):
            return TOMLError(ErrorCode.INVALID_TYPE)

        if not email_pattern.match(value):
            return TOMLError(ErrorCode.INVALID_EMAIL)

        if self.domains:
            domain = value.split("@")[-1]
            if domain not in self.domains:
                return TOMLError(ErrorCode.INVALID_DOMAIN)

        return None
