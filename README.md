# TOML Validator

![top language](https://img.shields.io/github/languages/top/marcusfrdk/tomlval)
![code size](https://img.shields.io/github/languages/code-size/marcusfrdk/tomlval)
![last commit](https://img.shields.io/github/last-commit/marcusfrdk/tomlval)
![issues](https://img.shields.io/github/issues/marcusfrdk/tomlval)
![contributors](https://img.shields.io/github/contributors/marcusfrdk/tomlval)
![PyPI](https://img.shields.io/pypi/v/tomlval)
![License](https://img.shields.io/github/license/marcusfrdk/tomlval)

A simple and easy to use TOML validator for Python.

## Installation

You can install the package from [PyPI](https://pypi.org/project/tomlval/):

```bash
pip install tomlval
```

The package is available for Python 3.11 and newer.

## Usage

### Handlers

Handlers are the validation functions used to validate the value of keys in the input data.

#### Types

A handler must be one of `type`, `Callable`. This means any object of type `type` is valid, and and `Callable`, such as `lambda` functions as well as named functions are valid.

#### Parameters

The handler will dynamically be passed either the `key` and/or `value` argument based of what parameters are defined. No parameters are also okay.

Examples of valid handlers are:

-   **Types:** `str`, `int`, `datetime.datetime`, ...
-   **Anonymous functions:** `lambda: ...`, `lambda key: ...`, `lambda value: ...`, `lambda key, value: ...`
-   **Named functions:** `def my_fn()`, `def my_fn(key)`, `def my_fn(value)`, `def my_fn(key, value)`

If a handler accepts any parameters which are not `key` or `value`, a `TOMLHandlerError` will be raised.

#### Return Types

A handler returns an error, meaning _nullish_ values tell the validator that the test passes. The reason for this design is that the handler may return error messages or any value your program needs.

### Schema

A schema is an _optional_ structure used to add functionality to the validator, this includes validation for missing keys and default handlers for keys.

#### Keys

Keys follow the TOML specification, meaning keys must be in either `snake_case` or `SCREAMING_SNAKE_CASE`. This project adds some special notation in the form of suffixing a key with `?` to make it optional, adding `[]` to the end to make the key an array and wildcard regex pattern support. The importance of keys are based of specificity, so `my.key` would dominate both `my.*` and `*`.

This means the following keys are examples of valid keys:

-   `name`, `user.name`: Specific key
-   `*_name`, `user.*`, `*name*`, `user.*.name`: Wildcard keys
-   `last_name?`, `user.name?`, `array?[].key`: Optional keys
-   `array[]`, `array?[]`, `array[].key`: Nested arrays

All keys can be written in dot-notation, meaning a deeply nested object/array can be written in a simpler form. For example:

```py
{
    "very": {
        "deeply": {
            "nested": {
                "object": {
                    "key": str
                }
            }
        }
    }
}
```

can be written as `"very.deeply.nested.object.key": str`. This notation also supports optionality and arrays. This would work by just suffixing the word with `?` and if an array, suffix the `?` with `[]`.

#### Defining a Schema

In order to define a new schema, you can use the following code as reference:

```py
from tomlval import TOMLSchema

def my_fn(key, value):
    return "some-error"

def default_handler() -> str:
    """ Default handler for all keys """
    return "invalid-key"

schema = TOMLSchema({
    "single_type": str,
    "multiple_types": (int, float),
    "single_handler": lambda: "error-message",
    "multiple_handlers": (lambda: "error-message", str, my_fn),
    "optional?": str
    "list_of_strings": [str],
    "nested_dictionary": {
        "key": str,
        ...
    },
    "nested_array": [
        {
            "key": str,
            ...
        },
        ...
    ],
})
```

_Note: When a nested array includes dictionaries with different structures, they will be merged. If the merge fails, a `TOMLSchemaMergeError` will be raised._

### Validator

The validator defines the blueprint for how data should be validated. This is defined in the optional schema, or handlers can be manually added using the `add_handler(key, fn)` method. Handlers, like keys, are prioritized based of the key priority.

#### Examples

##### Basic

This examples includes the most basic use case, where a default handler is defined manually:

```py
from tomlval import TOMLValidator

validator = TOMLValidator()
validator.add_handler("*", lambda: "invalid-key")
```

##### With a Schema

This example includes a schema, assume the schema is populated with the structure and handlers you require.

```py
from tomlval import TOMLValidator, TOMLSchema

schema = TOMLSchema({...})
validator = TOMLValidator(schema)
```

##### Customizing a Defined Schema

This example includes a case where you might have defined a _shared_ schema somewhere in your code but you need to customize specific keys:

```py
from tomlval import TOMLValidator
from .schema import schema

def validate_age(value):
    if value <= 0:
        return "value-to-low"
    return None

validator = TOMLValidator(schema)
validator.add_handler("user.age", validate_age)
```

##### Customizing The Default Callbacks

For some people, it might not be the best option to return an error message, and instead some other value might be preferred or even a more verbose error message. In this case, the `on_missing` and `on_type_mismatch` callbacks are changed:

```py
from tomlval import TOMLValidator
from .schema import schema

def on_missing(key: str):
    return f"'{key}' is missing"

def on_type_mismatch(key: str, expected: type, got: type)
    return f"The argument '{key}' expected type '{expected.__name__}', got '{got.__name__}'"

validator = TOMLValidator(
    schema,
    on_missing=on_missing,
    on_type_mismatch=on_type_mismatch
)
```

### Validation

Now that you have defined your schema and validator, the validator is now ready to be used on TOML data.

In order to use the validator, the `validate(data)` method is used. It accepts any dictionary as an argument and outputs a flat dictionary of all keys in dot-notation with each key's respective error value.

#### Examples

##### Validate File

This example shows a use-case where a TOML file is validated.

```py
import tomllib
from datetime import datetime
from pathlib import Path
from tomlval import TOMLSchema, TOMLValidator

# Read file
file_path = Path("example.toml")
with file_path.open("rb") as file:
    data = tomllib.load(file)

# Define schema
schema = TOMLSchema({
    "*_name": str,
    "age": lambda value: "invalid-age" if age <= 0 else None,
    "birthday": datetime,
    "*": lambda: "invalid-key"
})

# Define validator
validator = TOMLValidator(schema)

# Validate data
errors = validator.validate(data)
```

##### Validate Dictionary

Instead of loading a file, you might have pre-loaded TOML-data in the form of a dictionary.

```py
import tomllib
from datetime import datetime
from pathlib import Path
from tomlval import TOMLSchema, TOMLValidator
from .data import data

# Define schema
schema = TOMLSchema({
    "*_name": str,
    "age": lambda value: "invalid-age" if age <= 0 else None,
    "birthday": datetime,
    "*": lambda: "invalid-key"
})

# Define validator
validator = TOMLValidator(schema)

# Validate data
errors = validator.validate(data)
```

## License

This project is licensed under the MIT License - seea the [LICENSE](LICENSE) file for details.
