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

## Concepts

Before using the package, there are some concepts you may need to understand for the most optimal use of the package.

### Key

A key is the name of a field in a TOML file, such as `name`, `person.name`, etc. Keys must conform to the TOML specification, which means keys are either **snake_case** or **SCREAMING_SNAKE_CASE**. For the validator, keys may also include wildcards, such as `*name`, `person.*`, etc.

### Handler

A _handler_ is a function that is called for a certain key. Handlers can be of the following types:

-   Types, such as `int`, `str`, `float`.
-   Tuples/Lists of types, such as `(int, str)`, `[int, str]`.
-   Anonymous functions (`lambda`)
-   Named functions (Callable objects, such as `def my_handler(key, value): ...`)

The following argument configurations are supported:

-   `fn()`
-   `fn(key)`
-   `fn(value)`
-   `fn(key, value)`

If the handler has any other parameters than `key` or `value`, the validator will raise a `TOMLHandlerError`.

Handlers may return any type, but is is recommended to use the return type as an error message if the value is invalid. The validator considers a `None` return value a successful validation.

### Schema

The schema is used to give the validator default handlers and an ability to make sure certain keys exist. The schema is defined in the `TOMLSchema` class, and is passed to the `TOMLValidator` class. To create a schema, you pass a dictionary with the keys and their respective allowed types.

Here is an example of a schema:

```python
{
    "single_type": str,
    "list_of_strings": [str],
    "mixed_list:" [str, int],
    "multiple_types": (int, float),
    "optional?": str,
    "nested": {
        "key": str
    }
}
```

When a schema is defined, the validator will also check if values are missing and if their types are correct. If a handler is defined for a key, the validator will use the handler instead of the type defined in the schema.

### Validator

The validator is the core of the package. It is used to validate a TOML file. A schema is optionally passed to the validator, and handlers are added using the `add_handler` method. Once you feel ready, you can call the `validate` method with the data you want to validate as an argument to get a dictionary of errors.

Currently, there are two type of error structures, for type errors and all other errors.

Type errors are structured as follows:

```python
"key": (message, (value, expected_type, actual_type))
```

_`expected_type` and `actual_type` can be either `type` or `tuple[type]`_

All other errors have a slightly simpler structure:

```python
"key": (message, value)
```

The point of the validator is to parse the data and get the errors in a clean and easy way. **What you do with the errors is up to you.**

## Example

Here is a full example of how to use the validator.

```python
import pathlib
import tomllib
import datetime
from tomlval import TOMLValidator, TOMLSchema

# Load data from file
path = pathlib.Path("data.toml")

with path.open("rb") as file:
    data = tomllib.load(file)

# Use a dictionary
# data = {
#     "first_name": "John",
#     "last_name": "Doe",
#     "age": 25,
#     ...
# }

# Define schema (optional)
structure = {
    "first_name": str,
    "last_name": str,
    "age": int,
    "email": str,
    "phone": str,
    "birthday": datetime.datetime,
    "address": {
        "street": str,
        "city": str,
        "zip": int
    }
}

schema = TOMLSchema(structure) # If the struture is invalid, a TOMLSchemaError is raised

# Define validator
validator = TOMLValidator(schema)

# Add handlers
validator.add_handler("*_name", lambda key: None if key in ["first_name", "last_name"] else "invalid-key")
validator.add_handler("age", lambda value: None if 18 < value < 100 else "invalid-age")
validator.add_handler("*", lambda: "invalid-key")

# Validate the data
errors = validator.validate(data)
```

## Future Plans

Future plans are found in the [TODO](TODO.md) file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
