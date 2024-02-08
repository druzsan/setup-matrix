"""
Test `main.py`.
"""

from typing import Any

import pytest
import yaml.parser

from main import assert_valid_extra, assert_valid_matrix, parse_matrix


class TestAssertValidExtra:
    """
    Test `assert_valid_extra` function.
    """

    @pytest.mark.parametrize(
        "extra",
        [
            [],
            [{"foo": "bar"}],
            [{"foo": "bar", "bar": "baz"}],
            [{"foo": "bar"}, {"bar": "baz"}],
        ],
        ids=["empty", "single_variable", "multiple_variables", "multiple_combinations"],
    )
    def test_valid_extras(self, extra: list) -> None:
        assert_valid_extra(extra)

    @pytest.mark.parametrize(
        "extra",
        [{}, None, "foo", 0, 0.0, False],
        ids=["mapping", "null", "string", "int", "float", "bool"],
    )
    def test_invalid_extras(self, extra: Any) -> None:
        with pytest.raises(TypeError):
            assert_valid_extra(extra)

    @pytest.mark.parametrize(
        "extra",
        [[[]], [None], ["foo"], [0], [0.0], [False]],
        ids=["sequence", "null", "string", "int", "float", "bool"],
    )
    def test_invalid_combinations(self, extra: Any) -> None:
        with pytest.raises(TypeError):
            assert_valid_extra(extra)

    @pytest.mark.parametrize(
        "extra", [[{}], [{"foo": "bar"}, {}]], ids=["empty", "partial_empty"]
    )
    def test_empty_combinations(self, extra: Any) -> None:
        with pytest.raises(ValueError):
            assert_valid_extra(extra)

    @pytest.mark.parametrize(
        "extra",
        [[{None: "foo"}], [{0: "foo"}], [{0.0: "foo"}], [{False: "foo"}]],
        ids=["null", "int", "float", "bool"],
    )
    def test_invalid_combination_keys(self, extra: Any) -> None:
        with pytest.raises(TypeError):
            assert_valid_extra(extra)

    @pytest.mark.parametrize(
        "extra",
        [
            [{"foo": {}}],
            [{"foo": []}],
            [{"foo": None}],
            [{"foo": 0}],
            [{"foo": 0.0}],
            [{"foo": False}],
        ],
        ids=["mapping", "sequence", "null", "int", "float", "bool"],
    )
    def test_invalid_combination_values(self, extra: Any) -> None:
        with pytest.raises(TypeError):
            assert_valid_extra(extra)


class TestAssertValidMatrix:
    """
    Test `assert_valid_matrix` function.
    """

    @pytest.mark.parametrize(
        "matrix",
        [
            {"foo": ["bar", "baz"]},
            {"foo": ["bar", "baz"], "bar": ["baz", "foo", "bar"]},
            {"foo": ["bar", "baz"], "include": []},
            {"foo": ["bar", "baz"], "exclude": []},
            {"foo": ["bar", "baz"], "include": [{"foo": "bar"}, {"bar": "baz"}]},
            {"foo": ["bar", "baz"], "exclude": [{"foo": "bar"}, {"bar": "baz"}]},
            {
                "foo": ["bar", "baz"],
                "include": [{"foo": "bar"}, {"bar": "baz"}],
                "exclude": [{"foo": "bar"}, {"bar": "baz"}],
            },
            {"include": [{"foo": "bar"}, {"bar": "baz"}]},
            {"exclude": [{"foo": "bar"}, {"bar": "baz"}]},
            {
                "include": [{"foo": "bar"}, {"bar": "baz"}],
                "exclude": [{"foo": "bar"}, {"bar": "baz"}],
            },
        ],
    )
    def test_valid_matrix(self, matrix: dict) -> None:
        assert_valid_matrix(matrix)

    @pytest.mark.parametrize(
        "matrix",
        [None, {"include": []}, {"exclude": []}, {"include": [], "exclude": []}],
        ids=["empty", "empty_include", "empty_exclude", "empty_include_and_exclude"],
    )
    def test_empty_matrix(self, matrix: Any) -> None:
        with pytest.raises(RuntimeError):
            assert_valid_matrix(matrix)

    @pytest.mark.parametrize(
        "matrix",
        [[], "foo", 0, 0.0, False],
        ids=["sequence", "string", "int", "float", "bool"],
    )
    def test_invalid_matrix(self, matrix: Any) -> None:
        with pytest.raises(TypeError):
            assert_valid_matrix(matrix)

    @pytest.mark.parametrize(
        "matrix",
        [
            {None: ["foo", "bar"]},
            {0: ["foo", "bar"]},
            {0.0: ["foo", "bar"]},
            {False: ["foo", "bar"]},
        ],
        ids=["null", "int", "float", "bool"],
    )
    def test_invalid_combination_keys(self, matrix: Any) -> None:
        with pytest.raises(TypeError):
            assert_valid_matrix(matrix)

    @pytest.mark.parametrize(
        "matrix",
        [
            {"foo": {}},
            {"foo": None},
            {"foo": 0},
            {"foo": 0.0},
            {"foo": False},
        ],
        ids=["mapping", "null", "int", "float", "bool"],
    )
    def test_invalid_values_type(self, matrix: Any) -> None:
        with pytest.raises(TypeError):
            assert_valid_matrix(matrix)

    @pytest.mark.parametrize(
        "matrix",
        [{"foo": []}, {"foo": ["bar"], "bar": []}],
        ids=["empty", "partial_empty"],
    )
    def test_empty_values(self, matrix: Any) -> None:
        with pytest.raises(ValueError):
            assert_valid_matrix(matrix)

    @pytest.mark.parametrize(
        "matrix",
        [
            {"foo": [{}]},
            {"foo": [[]]},
            {"foo": [None]},
            {"foo": [0]},
            {"foo": [0.0]},
            {"foo": [False]},
        ],
        ids=["mapping", "sequence", "null", "int", "float", "bool"],
    )
    def test_invalid_values(self, matrix: Any) -> None:
        with pytest.raises(TypeError):
            assert_valid_matrix(matrix)


VALID_MATRICES_YAML = [
    """foo:
- bar
- baz""",
    """

foo:
  - bar
  - baz

""",
    """

        foo:
        - bar
        - baz

""",
    """{foo: [bar, baz], include: [{bar: baz}], exclude: [{baz: foo}]}""",
    """{'foo': ['bar', "baz"], "bar": ['baz', "foo"]}""",
    """foo: ['":{}[],&*#?|-<>=!%@`"', "':{}[],&*#?|-<>=!%@`'"]""",
    "foo: ['bar baz', 'baz    foo']",
]
VALID_MATRICES = [
    {"foo": ["bar", "baz"]},
    {"foo": ["bar", "baz"]},
    {"foo": ["bar", "baz"]},
    {"foo": ["bar", "baz"], "include": [{"bar": "baz"}], "exclude": [{"baz": "foo"}]},
    {"foo": ["bar", "baz"], "bar": ["baz", "foo"]},
    {"foo": ['":{}[],&*#?|-<>=!%@`"', "':{}[],&*#?|-<>=!%@`'"]},
    {"foo": ["bar baz", "baz    foo"]},
]


class TestParseMatrix:
    """
    Test `parse_matrix` function.
    """

    @pytest.mark.parametrize(
        "matrix_yaml, matrix", zip(VALID_MATRICES_YAML, VALID_MATRICES)
    )
    def test_valid_matrix(self, matrix_yaml: str, matrix: dict) -> None:
        parsed_matrix = parse_matrix(matrix_yaml)
        print(parsed_matrix)
        print(matrix)
        assert parsed_matrix == matrix

    @pytest.mark.parametrize(
        "matrix_yaml",
        [
            "",
            "foo:",
            "[]",
            "foo",
            "{}",
            "foo: []",
            "foo: [{}]",
            "include: []",
            "exclude: {}",
            "include: foo",
            "exclude: [{}]",
        ],
    )
    def test_invalid_matrix(self, matrix_yaml: str) -> None:
        with pytest.raises((RuntimeError, TypeError, ValueError)):
            parse_matrix(matrix_yaml)

    @pytest.mark.parametrize("matrix_yaml", ["][", "}{"])
    def test_invalid_matrix_syntax(self, matrix_yaml: str) -> None:
        with pytest.raises(yaml.parser.ParserError):
            parse_matrix(matrix_yaml)
