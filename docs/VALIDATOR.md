# Validator

The validator is the object that performs the actual validation of the schema against the data. It uses the optionally defined schema alongside manually added [handlers](HANDLER.md) to validate the data and returns a dictionary of errors.

## Methods

### `validate(data: Dict[str, Any]) -> Dict[str, Any]`

Validate the provided data against the defined schema and returns a flat dictionary of errors.

### `add_handler(key: str, handler: Handler) -> None`

Add a handler for a specific key to the validator. This is an alternative to defining handlers in the schema.

## Parameters

Parameters are passed to the validator to handle specific cases of validation, such as type mismatches, missing keys, or pattern mismatches. By default, the callbacks will return a specific error code, but you can define your own functions to handle these cases.

### `on_missing(key: str) -> Any`

This parameter is a callback function that is called when a required key is missing from the data. It receives the key as an argument and can return any value.

### `on_type_mismatch(key: str, expected: type, got: type) -> Any`

This parameter is a callback function that is called when a type mismatch occurs. It receives the key, the expected type, and the actual type as arguments and can return any value.

### `on_pattern_mismatch(key: str, value: Any, pattern: re.Pattern) -> Any`

This parameter is a callback function that is called when a string does not match the expected `re.Pattern`. It receives the key, the value, and the pattern as arguments and can return any value.
