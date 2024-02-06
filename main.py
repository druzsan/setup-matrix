#!/usr/bin/env python3
import os

import yaml


def debug(text: str) -> None:
    print(f"::debug::{text}")


def output(name: str, value: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="UTF-8") as output_file:
        output_file.write(f"{name}={value}\r\n")


def setenv(name: str, value: str) -> None:
    with open(os.environ["GITHUB_ENV"], "a", encoding="UTF-8") as output_file:
        output_file.write(f"{name}={value}\r\n")


if __name__ == "__main__":
    matrix = yaml.safe_load(os.environ["INPUT_MATRIX"])
    include = yaml.safe_load(os.environ["INPUT_INCLUDE"])
    exclude = yaml.safe_load(os.environ["INPUT_EXCLUDE"])

    print("foo")
    debug("bar")
    output("matrix", "{}")
    setenv("MATRIX", "{}")

    if matrix is None and include is None and exclude is None:
        raise RuntimeError(
            "At least one of matrix, include or exclude should be not empty"
        )

    print(matrix)
    print(include)
    print(exclude)
