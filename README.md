# TOML Validator

![top language](https://img.shields.io/github/languages/top/marcusfrdk/tomlval)
![code size](https://img.shields.io/github/languages/code-size/marcusfrdk/tomlval)
![last commit](https://img.shields.io/github/last-commit/marcusfrdk/tomlval)
![issues](https://img.shields.io/github/issues/marcusfrdk/tomlval)
![contributors](https://img.shields.io/github/contributors/marcusfrdk/tomlval)
![PyPI](https://img.shields.io/pypi/v/tomlval)
![License](https://img.shields.io/github/license/marcusfrdk/tomlval)
![Downloads](https://static.pepy.tech/badge/tomlval)
![Monthly Downloads](https://static.pepy.tech/badge/tomlval/month)

A package used for validating TOML data against a schema and manually added handlers. It is designed to be flexible and easy to use, allowing you to customize the validation process to fit your needs.

## Installation

You can install the package from [PyPI](https://pypi.org/project/tomlval/):

```bash
pip install tomlval
```

The package is available for Python 3.11 and newer.

## Concepts

### Handlers

A handler is a validation function used by the validator to validate the value of a key. Handlers can be defined in a [schema](docs/SCHEMA.md) or added directly to the [validator](docs/VALIDATOR.md) using the `add_handler(key, fn) method.

You can read more about handlers in the [handler documentation](docs/HANDLER.md).

### Schema

A schema is a collection of keys and their associated handlers. It is defined as a dictionary where the keys are specific- or wildcard keys and the values are the functions ([handlers](docs/HANDLER.md)).

You can read more about schemas in the [schema documentation](docs/SCHEMA.md).

### Validator

The validator is the object that performs the actual validation on the data. It uses the optionally defined schema alongside manually added [handlers](docs/HANDLER.md) to validate the data and returns a dictionary of errors.

You can read more about the validator in the [validator documentation](docs/VALIDATOR.md).

## Examples

```python
from tomlval import TOMLSchema, TOMLValidator

# Define a schema
schema = TOMLSchema({
    "name": str,
    "age": int,
})

# Sample TOML data
data = {
    "name": "Alice",
    "age": 30,
}

# Create a validator
validator = TOMLValidator(schema=schema)

# Validate the data
errors = validator.validate(data)
```

```python
from tomlval import TOMLSchema, TOMLValidator

# Define a schema
schema = TOMLSchema({
    "email?": str,  # Optional email
    "username": lambda value: "invalid-username" if len(value) < 3 else None,  # Custom handler
})

# Sample TOML data
data = {
    "username": "ab",
}

# Create a validator
validator = TOMLValidator(schema=schema)

# Validate the data
errors = validator.validate(data)
print(errors)
```

```python
import re
from datetime import datetime
from tomlval import TOMLSchema, TOMLValidator

# Regex patterns
username_pattern = re.compile(r"^[a-zA-Z0-9_]+$")
email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Sample TOML data
data = {
    "first_name": "John",
    "last_name": "Doe",
    "age": 25,
    "email": "john.doe@example.com",
    "username": "john_doe",
    "birthday": datetime(1999, 1, 1),
    "is_active": True,
    "scores": [85, 92, 78],
    "preferences": {
        "theme": "dark",
        "notifications": True,
        "language": "en"
    },
    "social_profiles": [
        {"platform": "twitter", "handle": "@johndoe"},
        {"platform": "github", "handle": "johndoe"}
    ],
    "work_history": [
        {
            "company": "TechCorp",
            "position": "Developer",
            "skills": [{"name": "Python", "level": 8}, {"name": "JavaScript", "level": 7}]
        }
    ],
    "metadata": {
        "created_at": datetime.now(),
        "tags": ["user", "premium"]
    }
}

# Define a schema
schema = TOMLSchema({
    # Basic type validation
    "first_name": str,
    "age": (int, float),  # Multiple types
    "birthday": datetime,
    "is_active": bool,

    # Optional keys
    "middle_name?": str,
    "phone?": str,

    # Regex pattern validation
    "username": username_pattern,
    "email": email_pattern,

    # Custom handlers
    "last_name": lambda value: "too-short" if len(value) < 2 else None,
    "age": lambda value: "invalid-age" if not (0 < value < 150) else None,
    "email": lambda key: f"missing-{key}" if not key else None,
    "username": lambda key, value: f"invalid-{key}" if len(value) < 3 else None,

    # List validation
    "scores": [int],  # List of integers
    "tags?": [str],   # Optional List of strings

    # Nested object validation
    "preferences": {
        "theme": str,
        "notifications": bool,
        "language?": str  # Optional nested key
    },

    # List of objects
    "social_profiles": [
        {
            "platform": str,
            "handle": lambda value: "invalid-handle" if not value.startswith("@") else None
        }
    ],

    # Deeply nested list of objects
    "work_history": [
        {
            "company": str,
            "position": str,
            "skills": [
                {
                    "name": str,
                    "level": lambda value: "invalid-level" if not (1 <= value <= 10) else None
                }
            ]
        }
    ],

    # Optional nested object
    "metadata?": {
        "created_at": datetime,
        "tags": [str],
        "version?": float
    },

    # Wildcard patterns
    "*_name": str,                    # Matches first_name, last_name, etc.
    "preferences.*": lambda: None,    # Matches any key in preferences
    "*_profiles": [dict],             # Matches social_profiles, etc.

    # Keys within lists
    "scores[]": int,                  # Individual List elements
    "work_history[].company": str,    # Nested List element validation
    "social_profiles[].platform": lambda value: "unsupported" if value not in ["twitter", "github", "linkedin"] else None,

    # Optional List elements
    "work_history[]?": dict,          # Optional List elements
    "preferences?.*": str,            # Optional wildcard in optional object

    # Catch-all handler
    "*": lambda: "invalid-key"
})

# Custom callback functions
def on_missing_key(key: str) -> str:
    return f"Missing key '{key}'"

def on_type_mismatch(key: str, expected, got) -> str:
    return f"Key '{key}' expected {expected.__name__} but got {got.__name__}"

def on_pattern_mismatch(key: str, pattern) -> str:
    return f"Key '{key}' does not match pattern {pattern.pattern}"

# Override default handlers
validator = TOMLValidator(
    schema=schema,
    on_missing=on_missing_key,
    on_type_mismatch=on_type_mismatch,
    on_pattern_mismatch=on_pattern_mismatch
)

# Manual handlers
validator.add_handler("some.key", lambda value: "custom-error" if value == "invalid" else None)

# Validate
errors = validator.validate(data)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
