"""Error codes for TOML validation."""

from enum import Enum


class ErrorCode(Enum):
    """Enum for TOML error codes."""

    INVALID_TYPE = "invalid-type"
    INVALID_KEY = "invalid-key"
    INVALID_EMAIL = "invalid-email"
    INVALID_DOMAIN = "invalid-domain"
    INVALID_LITERAL_VALUE = "invalid-literal-value"
    INVALID_ARRAY_ELEMENT = "invalid-array-element"
    INVALID_LENGTH = "invalid-length"
    MISSING_KEY = "missing-key"
    VALIDATION_FAILURE = "validation-failure"
    REGEX_MISMATCH = "regex-mismatch"
    DATETIME_PARSE_ERROR = "datetime-parse-error"
    FUNCTION_EXECUTION_ERROR = "function-execution-error"
    UNKNOWN_ERROR = "unknown-error"
    TOO_LARGE = "too-large"
    TOO_SMALL = "too-small"
    TOO_SHORT = "too-short"
    TOO_LONG = "too-long"
