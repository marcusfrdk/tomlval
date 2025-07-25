"""Error returned by the TOML validator."""

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


class TOMLError:
    """Error returned by the TOML validator."""

    def __init__(self, code: str) -> None:
        """
        Initialize the TOMLError.

        Args:
            code: The error code
        """
        self.code = code

    def __eq__(self, other):
        if not isinstance(other, TOMLError):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    def __str__(self) -> str:
        return self.code

    def __repr__(self) -> str:
        return f"<TOMLError {self.code}>"
