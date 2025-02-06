""" An example schema for the 'full_spec.toml' file. """

from tomlval import TOMLSchema

full_spec_schema = TOMLSchema(
    {
        "string_basic": str,
        "string_multiline": str,
        "string_literal": str,
        "string_multiline_literal": str,
        "int_positive": int,
        "int_negative": int,
        "int_hex": int,
        "int_oct": int,
        "int_bin": int,
        "float_simple": float,
        "float_exponent": float,
        "float_negative_exponent": float,
        "float_with_sign": float,
        "float_with_underscores": float,
        "bool_true": bool,
        "bool_false": bool,
        "datetime_utc": str,
        "datetime_offset": str,
        "datetime_with_fraction": str,
        "local_datetime": str,
        "local_date": str,
        "local_time": str,
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
        "escape_newline": str,
        "escape_tab": str,
        "escape_unicode": str,
        "int_large": int,
        "float_large": float,
        "bool_case_sensitive": bool,
        "table": {"key": str, "subtable": {"nested_key": int}},
        "array_of_tables": [
            {"name": str, "value": int},
        ],
        "nested_array": [
            {"name": str, "inner": [{"name": str}, {"name": str}]},
        ],
    }
)

if __name__ == "__main__":
    print(full_spec_schema)
