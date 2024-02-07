#!/usr/bin/env python3
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


def parse_include_exclude(input_include_exclude: str) -> list:
    include_exclude = yaml.load(input_include_exclude, Loader=yaml.loader.BaseLoader)
    if include_exclude is None:
        return []
    if not isinstance(include_exclude, list):
        raise TypeError(
            f"Include/exclude must be a list, but {type(include_exclude)} received."
        )
    for combination in include_exclude:
        if not isinstance(combination, dict):
            raise TypeError(
                f"Each include/exclude combination must a dict, but "
                f"{type(combination)} received."
            )
        for variable, value in combination.items():
            if not isinstance(variable, str):
                raise TypeError(
                    f"Include/exclude combination variables must be strings, "
                    f"but variable of type {type(variable)} received."
                )
            if not isinstance(value, str):
                raise TypeError(
                    f"Include/exclude combination values must be strings, but "
                    f"{type(value)} received for variable '{variable}'."
                )
    return include_exclude


def assert_valid_extra(extra: Any) -> None:
    if not isinstance(extra, list):
        raise TypeError(
            f"Include/exclude must be an array (Python list), but Python "
            f"{type(extra)} received."
        )


def assert_valid_matrix(matrix: Any) -> None:
    if not isinstance(matrix, dict):
        raise TypeError(
            f"Matrix must be a mapping (Python dict), but Python "
            f"{type(matrix)} received."
        )
    for variable, values in matrix.items():
        if not isinstance(variable, str):
            raise TypeError(
                f"Matrix variables must be strings, but {type(variable)} received."
            )
        if variable in ("include", "exclude"):
            assert_valid_extra(values)


def parse_matrix(input_matrix: str) -> dict:
    # Parse every YAML scalar as a string
    matrix = yaml.load(input_matrix, Loader=yaml.loader.BaseLoader)
    print(matrix)

    if matrix is None:
        raise RuntimeError("Strategy matrix must define at least one combination.")

    return matrix


if __name__ == "__main__":
    matrix = parse_matrix(os.environ["INPUT_MATRIX"])

    print(yaml.dump({"matrix": matrix}))

    # output_matrix = json.dumps(matrix)
    output_matrix = "{'include':[],'exclude':[]}"

    output("matrix", output_matrix)
    setenv("MATRIX", output_matrix)
