""" An example schema for the 'full_spec.toml' file. """

from datetime import datetime

from tomlval import TOMLSchema

full_spec_schema = TOMLSchema(
    {
        "string_*": str,
        "int_*": int,
        "float_*": float,
        "bool_*": bool,
        "*datetime_*": datetime,
        "array_numbers": [int],
        "array_strings": [str],
        "array_mixed": [int, str, float, bool],
        "array_multiline": [str],
        "inline_table": {"key1": str, "key2": int, "key3": bool},
        "dotted": {
            "key": {"value": str},
            "numbers": {"list": [int]},
        },
        "unicode_text": str,
        "escape_*": str,
        "table": {"key": str, "subtable": {"nested_key": int}},
        "array_of_tables": [{"name": str, "value": int}],
        "nested_array": [
            {"name": str, "inner": [{"name": str}, {"name": str}]},
        ],
    }
)

if __name__ == "__main__":
    print(full_spec_schema)
