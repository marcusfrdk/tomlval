# Handler

A handler is a validation function which is used to validate the value of a key.

## Priority

Handlers are ordered by priority. If two or more handlers target the same key, the most specific handler will be used. The order is as follows:

1. **Specific keys:** `user.name`, `key`, ...
2. **Hybrid Keys**: `user.*`, `user.*_name`, ...
3. **Wildcard keys:** `*`, `*name*`, `*_name`, ...

If two or more handlers have the same priority, the last added handler will be used.

## Types

A handler must be one of the following types:

-   **Primitives:** `str`, `int`, `float`, `bool`, ...
-   **Objects:** `datetime.datetime`, `re.Pattern`, ...
-   **Functions:** Both anonymous functions (lambdas) and named functions (def) are valid.

## Parameters

The handler function will accept a combination of the parameters `key` and `value`, depending on how the handler is defined. If the handler accepts only the `value` parameter, the `value` will be passed to the handler. Likewise, if the handler accepts only the `key` parameter, the `key` will be passed to the handler. If both parameters are accepted, both will be passed to the handler and if none are accepted, the handler will be called without any parameters.

## Return

Any _truthy_ value is considered an error, meaning values which are not `None`, `False`, `0`, `""`, `[]`, or `{}` will indicate a validation failure. This design allows the handler to return error messages or any value your program needs.

## Examples

```python
empty_handler = lambda: "This is a static error."
key_handler = lambda key: f"Error in the key '{key}'."
value_handler = lambda value: f"Error in the value '{value}'."
key_value_handler = lambda key, value: f"Error in the key '{key}' with value '{value}'."
```

```python
from typing import Any

def empty_handler():
    return "This is a static error."

def key_handler(key: str):
    return f"Error in the key '{key}'."

def value_handler(value: Any):
    return f"Error in the value '{value}'."

def key_value_handler(key: str, value: Any):
    return f"Error in the key '{key}' with value '{value}'."
```
