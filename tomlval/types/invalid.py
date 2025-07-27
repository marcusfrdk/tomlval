"""Invalid type for TOML values."""

from tomlval.types._toml_type import TOMLType


class InvalidMeta(type):
    """Metaclass for Invalid to control class representation."""

    def __str__(cls) -> str:
        return "<Invalid>"

    def __repr__(cls) -> str:
        return "<Invalid>"


class Invalid(TOMLType, metaclass=InvalidMeta):
    """Represents an invalid/forbidden value in a TOML schema."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = True
        return cls._instance

    def __str__(self) -> str:
        return "<Invalid>"

    def __repr__(self) -> str:
        return str(self)
