#!/usr/bin/env python3
import json
import os
from typing import Any

import yaml


def output(name: str, value: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="UTF-8") as output_file:
        output_file.write(f"{name}={value}\r\n")


def setenv(name: str, value: str) -> None:
    with open(os.environ["GITHUB_ENV"], "a", encoding="UTF-8") as output_file:
        output_file.write(f"{name}={value}\r\n")


def parse_base_matrix(input_matrix: str) -> dict:
    matrix = yaml.load(input_matrix, Loader=yaml.loader.BaseLoader)
    if matrix is None:
        return {}
    if not isinstance(matrix, dict):
        raise TypeError(f"Matrix must be a dict, but {type(matrix)} received.")
    for variable, values in matrix.items():
        if not isinstance(variable, str):
            raise TypeError(
                f"Matrix variables must be strings, but variable of type "
                f"{type(variable)} received."
            )
        for reserved_name in ("include", "exclude"):
            if variable == reserved_name:
                raise ValueError(f"Variable name '{reserved_name}' is reserved.")
        if not isinstance(values, list):
            raise TypeError(
                f"Matrix values must be lists, but {type(values)} received "
                f"for variable '{variable}'."
            )
        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    f"Each matrix value must be a string, but value of type "
                    f"{type(values)} received for variable '{variable}'."
                )
    return matrix


def assert_valid_extra(extra: Any) -> None:
    """
    Validate strategy include/exclude.
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
    print(matrix)

    assert_valid_matrix(matrix)

    return matrix


if __name__ == "__main__":
    matrix = parse_matrix(os.environ["INPUT_MATRIX"])

    print(yaml.dump({"matrix": matrix}))

    output_matrix = json.dumps(matrix)

    output("matrix", output_matrix)
    setenv("MATRIX", output_matrix)
