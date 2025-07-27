"""Error returned by the TOML validator."""

from typing import Union

from tomlval.errors.error_code import ErrorCode

INVALID_TYPE = "invalid-type"
INVALID_KEY = "invalid-key"
MISSING_KEY = "missing-key"
VALIDATION_FAILURE = "validation-failure"
INVALID_ARRAY_ELEMENT = "invalid-array-element"
REGEX_MISMATCH = "regex-mismatch"
DATETIME_PARSE_ERROR = "datetime-parse-error"
FUNCTION_EXECUTION_ERROR = "function-execution-error"
UNKNOWN_ERROR = "unknown-error"
INVALID_LITERAL_VALUE = "invalid-literal-value"
TOO_LARGE = "too-large"
TOO_SMALL = "too-small"
TOO_SHORT = "too-short"
TOO_LONG = "too-long"
INVALID_EMAIL = "invalid-email"
INVALID_DOMAIN = "invalid-domain"


class TOMLError:
    """Error returned by the TOML validator."""

    def __init__(self, code: Union[str, ErrorCode]) -> None:
        """
        Initialize the TOMLError.

        Args:
            code: The error code
        """
        if isinstance(code, str):
            code = ErrorCode(code)
        elif not isinstance(code, ErrorCode):
            raise ValueError(
                "The argument for a TOMLError must "
                "be a string or ErrorCode instance."
            )

        self.code = code

    def __eq__(self, other):
        if not isinstance(other, TOMLError):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    def __str__(self) -> str:
        if isinstance(self.code, ErrorCode):
            return self.code.value
        return self.code

    def __repr__(self) -> str:
        return f"<TOMLError {self.code}>"
