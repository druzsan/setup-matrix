#!/usr/bin/env python3
import json
import os

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
                f"for variable {variable}."
            )
        for value in values:
            if not isinstance(value, str):
                raise TypeError(
                    f"Each matrix value must be a string, but value of type "
                    f"{type(values)} received for variable {variable}."
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


def parse_matrix(input_matrix: str, input_include: str, input_exclude: str) -> dict:
    matrix = parse_base_matrix(input_matrix)
    include = parse_include_exclude(input_include)
    exclude = parse_include_exclude(input_exclude)

    if not matrix and not include and not exclude:
        raise RuntimeError(
            "At least one of 'matrix', 'include' or 'exclude' arguments should be set."
        )

    if include:
        matrix["include"] = include
    if exclude:
        matrix["exclude"] = exclude
    return matrix


if __name__ == "__main__":
    matrix = parse_matrix(
        os.environ["INPUT_MATRIX"],
        os.environ["INPUT_INCLUDE"],
        os.environ["INPUT_EXCLUDE"],
    )

    print(yaml.dump({"matrix": matrix}))

    output_matrix = json.dumps(matrix)

    output("matrix", output_matrix)
    setenv("MATRIX", output_matrix)
