#!/usr/bin/env python3
"""
Parse strategy matrix in GitHub Action.
"""
import json
import os
from typing import Any

import yaml


def output(name: str, value: str) -> None:
    """
    Write out an GitHub Action output.
    """
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="UTF-8") as output_file:
        output_file.write(f"{name}={value}\r\n")


def setenv(name: str, value: str) -> None:
    """
    Write out an GitHub Action environment variable.
    """
    with open(os.environ["GITHUB_ENV"], "a", encoding="UTF-8") as output_file:
        output_file.write(f"{name}={value}\r\n")


def assert_valid_extra(extra: Any) -> None:
    """
    Validate strategy matrix include/exclude.
    """
    if not isinstance(extra, list):
        raise TypeError(
            f"Include/exclude must be a sequence (Python list), but Python "
            f"{type(extra)} received."
        )
    for combination in extra:
        if not isinstance(combination, dict):
            raise TypeError(
                f"Each include/exclude combination must a mapping (Python "
                f"dict), but Python {type(combination)} received."
            )
        for variable, value in combination.items():
            if not isinstance(variable, str):
                raise TypeError(
                    f"Include/exclude variables must be strings, but "
                    f"Python {type(variable)} received."
                )
            if not isinstance(value, str):
                raise TypeError(
                    f"Each include/exclude value must be a string, but Python "
                    f"{type(value)} received for variable '{variable}'."
                )


def assert_valid_matrix(matrix: Any) -> None:
    """
    Validate strategy matrix.
    """
    if matrix is None:
        raise RuntimeError("Strategy matrix must define at least one combination.")
    if not isinstance(matrix, dict):
        raise TypeError(
            f"Matrix must be a mapping (Python dict), but Python "
            f"{type(matrix)} received."
        )
    for variable, values in matrix.items():
        if not isinstance(variable, str):
            raise TypeError(
                f"Matrix variables must be strings, but Python "
                f"{type(variable)} received."
            )
        if variable in ("include", "exclude"):
            assert_valid_extra(values)
        else:
            if not isinstance(values, list):
                raise TypeError(
                    f"Matrix values must be sequences (Python lists), but "
                    f"Python {type(values)} received for variable '{variable}'."
                )
            if not values:
                raise ValueError(f"No values received for variable '{variable}'.")
            for value in values:
                if not isinstance(value, str):
                    raise TypeError(
                        f"Each matrix value must be a string, but Python "
                        f"{type(value)} received for variable '{variable}'."
                    )
    # The whole matrix, one of or both include and exclude are empty.
    if not matrix or all(not values for values in matrix.values()):
        raise RuntimeError("Strategy matrix must define at least one combination.")


def parse_matrix(input_matrix: str) -> dict:
    """
    Parse strategy matrix from string and validate it.
    """
    # Parse every YAML scalar as a string
    matrix = yaml.load(input_matrix, Loader=yaml.loader.BaseLoader)

    assert_valid_matrix(matrix)

    return matrix


def main() -> None:
    """
    Parse strategy matrix from GitHub Action input ('matrix'), parse and
    validate it, print it out and set it as output ('matrix') and as
    environment variable ('MATRIX').
    """
    matrix = parse_matrix(os.environ["INPUT_MATRIX"])

    print(yaml.dump({"matrix": matrix}, sort_keys=False))

    output_matrix = json.dumps(matrix)

    output("matrix", output_matrix)
    setenv("MATRIX", output_matrix)


if __name__ == "__main__":
    main()
