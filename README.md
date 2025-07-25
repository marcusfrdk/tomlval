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

A flexible, easy-to-use, and dependency-free Python library for validating TOML data against custom schemas.

## Features

-   **Full TOML support**: Validates TOML data against custom schemas, ensuring compliance with the [TOML specification](https://toml.io/en/).
-   **Dependency-free**: No external dependencies, making it lightweight and easy to integrate.
-   **Flexible**: Supports custom schemas with optional fields and type validation.
-   **Easy to use**: Simple API for defining schemas and validating data.
-   **Type hints**: Utilizes Python's type hints for schema definitions, making code more readable and maintainable.

## Installation

You can install the package from [PyPI](https://pypi.org/project/tomlval/):

```bash
pip install tomlval
```

The package is available for Python 3.10 and newer.

## Usage

### Basic Example

```python
import re
from datetime import datetime
from tomlval import TOMLSchema, Optional, Invalid, Literal

schema = TOMLSchema({
    "*": Invalid # Catch-all
})
```

## Testing

Test dependencies are installed with the `dev` extra:

```bash
pip install tomlval[dev]
```

Run the tests with:

```bash
pytest
```

## Contributing

Contributions are welcome. If you have suggestions for improvements or find bugs, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
