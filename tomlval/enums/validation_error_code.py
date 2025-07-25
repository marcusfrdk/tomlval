"""Enum for validation errors in TOML schema validation."""

from enum import Enum


class ValidationErrorCode(Enum):
    """Enum for validation error types with custom messages."""

    INVALID_TYPE = "invalid-type"
    INVALID_KEY = "invalid-key"
    MISSING_KEY = "missing-key"
    VALIDATION_FAILURE = "validation-failure"
    INVALID_ARRAY_ELEMENT = "invalid-array-element"
    INVALID_TUPLE_TYPE = "invalid-tuple-type"
    REGEX_MISMATCH = "regex-mismatch"
    DATETIME_PARSE_ERROR = "datetime-parse-error"
    FUNCTION_EXECUTION_ERROR = "function-execution-error"
    UNKNOWN_ERROR = "unknown-error"
