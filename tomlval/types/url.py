"""Represents a URL in the schema."""

# pylint: disable=too-many-arguments

from typing import List, Optional

from tomlval.errors.error_code import ErrorCode
from tomlval.types._toml_error import TOMLError
from tomlval.types._toml_type import TOMLType


class Url(TOMLType):
    """Represents a URL in the schema."""

    def __init__(
        self,
        *,
        allow_protocol: bool = True,
        allow_localhost: bool = True,
        allow_ip_address: bool = True,
        allow_port: bool = True,
        allow_path: bool = True,
        allow_query_params: bool = True,
        allow_fragment: bool = True,
        allowed_protocols: Optional[List[str]] = None,
        allowed_domains: Optional[List[str]] = None,
        allowed_ports: Optional[List[int]] = None,
    ) -> None:
        """
        Initialize the Url type.

        Args:
            ...

        Raises:
            ...
        """


    def __str__(self) -> str:
        return "<Url>"

    def __repr__(self) -> str:
        return str(self)

    def validate(self, value: str):
        if not isinstance(value, str):
            return TOMLError(ErrorCode.INVALID_TYPE)

        return None
