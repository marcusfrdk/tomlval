# Schema

A schema is a mapping of keys to handlers which are used to validate the values of those keys. The schema is defined as a dictionary where the keys are specific- or wildcard keys and the values are the functions that will validate the values of those keys.

## Keys

A key in the schema will match the key in the TOML data. Keys can be specific, such as `user.name`, `my.nested.key` or `key`, or they can be wildcard keys, such as `user.*`, `user.*_name` or `*`. Wildcard keys can match any key that fits the pattern, allowing for flexible validation of nested structures.

### Format

All keys must be in either `snake_case` or `SCREAMING_SNAKE_CASE`, as per the TOML specification. This means keys like `user_name`, `USER_NAME`, `my.nested.key`, and `MY.NESTED.KEY` are valid, but keys like `userName`, `UserName`, or `myNestedKey` are not valid. This is to ensure consistency and compatibility with TOML standards. However, a small variation is allowed to enable features such as _optionality_, _arrays_ and _wildcards_.

### Optionality

Keys can also be marked as optional by appending a `?` to the key, such as `user.name?`, `my.nested.key?` or `key?`. This will allow the validator to skip validation for that key if it is not present in the data.

### Arrays

Keys can also be marked as arrays by appending `[]` to the key. For example, `users[].name` would match the `name` key in each object in the `users` array.

If a key should be both optional and an array, it can be written as `users?[]` or `users[].name?`. This allows for flexible validation of arrays and nested structures.

### Nesting

Keys can be nested using dot notation. For example, `user.address.street` would match the `street` key in the `address` object of the `user` object.

All nested keys support optionality and arrays, meaning `user.address.street?` or `user.address.street[]` are valid keys.

#### Merging

If a schema includes nested keys that have different structures, they will be merged. An example of this is:

```python

schema = TOMLSchema({
    "user: {
        "name": str
    },
    "user": {
        "age": int
    }
)
```

will turn into:

```python
schema = TOMLSchema({
    "user": {
        "name": str,
        "age": int
    }
})
```

If a merge fails, such as complex incompatible types (i.e. specific cases of array merges), a `TOMLSchemaMergeError` will be raised.

### Wildcards

Wildcard syntax is supported in keys in any position, meaning `user.*.name`, `*.name`, `user.*_name` and `*name*` are all valid keys and will match anything that fits the pattern. This is especially useful for validating keys where you might have multiple variations of a key, such as using `user.*_name` instead of `user.first_name` and `user.last_name`.

## Values

The schema values are [handlers](HANDLER.md) that will be applied to the values of the keys.

## Example

```python
import re
from datetime import datetime
from tomlval import TOMLSchema

schema = TOMLSchema({
    "name": str, # single type
    "age": (int, float), # multiple types
    "email": re.compile(...), # regex pattern
    "is_student?": bool, # optional boolean
    "scores[]": int, # array of integers
    "scores[].subject": str, # nested array with specific key
    "user": {
        "name": str, # nested key (same as "user.name": str)
    },
    "nested": [
        {
            "key": str # nested array with specific key (same as "nested[].key": str
        }
    ]
    "birthdate": datetime, # datetime object
    "*": lambda: ..., # catch-all handler
})
```
