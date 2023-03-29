# Build Matrix

GitHub action to create reusable dynamic job matrices for your workflows.

This action adresses a wide known problem of reusing the same job matrix
multiple times or even generating a matrix on the fly.

The main goal of this action is to be as much compatible with built-in
[GitHub matrices](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
as possible and thus allow you a smooth transition in your workflow.

## Basic usage

```yaml
jobs:
  build-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.build.outputs.matrix }}
    steps:
      - id: build
        uses: druzsan/build-matrix@v1
        with:
          matrix: |
            os: ubuntu-latest windows-latest macos-latest,
            python-version: 3.8 3.9 3.10
  setup-python:
    needs: build-matrix
    strategy:
      matrix: ${{ fromJson(needs.build-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
      - run: python --version
```

## Inputs

Inputs are the same as for the built-in matrix, but their syntax is slightly
different.

All inputs are optional with empty strings as default, but at least one of the
three inputs must be specified.

Only strings are allowed as GitHub action inputs, but you can use any
whitespaces including newlines for word separation in all inputs. It is
recommended to use (any) YAML multiline strings to unclutter your inputs, e.g.:

```yaml
with:
  matrix: |
    node-version: 12 14 16
  include: |
    node-version: 16
    npm: 6
```

All words themselves must not contain any whitespaces, colons and commas. All
other characters are allowed, but valid behaviour can not be validated for all
possible characters, so be aware that both input parsing and later matrix usage
could be affected by some edge cases.

### `matrix`

Optional base matrix configuration with the following syntax:

```
variable-1: value value <...>,
variable-2: value value <...>,
            <...>
variable-n: value value <...>[,]
```

Variable names must be unique and differ from exact 'include' and 'exclude'
strings reserved by the built-in matrix.

### `include`

Optioal extra matrix configurations to add to the base matrix. Must have the following
syntax:

```
variable-i: value variable-j: value <...>,
                   <...>
variable-k: value variable-l: value <...>[,]
```

Variable names in each configuration

### `exclude`

Optional matrix configurations to exclude from the base matrix. Have the same syntax and
restrictions as [`include`](#include).

## Outputs

Parsed matrix is printed inside the action's step as a pretty formated YAML
using `yq`, so you can visually inspect it.

### `matrix`

valid JSON matrix ready to be set as `jobs.<job_id>.outputs` used in
`jobs.<job_id>.strategy`:

```yaml
matrix: ${{ fromJson(needs.<job_id>.outputs.matrix) }}
```

## Errors

Not only syntax validity, but also built-in matrix' restrictions are checked. If
you find a case where either of the checks does not work, feel free to report it
in and issue.

Error logs try to give as much infomation on problem as possible.

## Advanced usage

### Reuse a matrix

Sometimes you need to run different jobs os the same set of configurations, e.g.
install python dependencies, check code quality and run unit tests.

<details>
    <summary>Solution using the built-in matrix</summary>

```yaml
jobs:
  # No matrix build
  # Setup python environment and cache installed packages
  setup-python:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
          cache: pip
      - run: python -m pip install -r requirements.txt
  # Check code quality
  check-code:
    needs: setup-python
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
          cache: pip
      - run: python -m pip install -r requirements.txt
      - run: black --check .
      - run: pylint .
  # Test code
  unit-test:
    needs: setup-python
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.8', '3.9', '3.10']
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
          cache: pip
      - run: pytest
```

</details>

```yaml
jobs:
  # Build matrix
  build-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.build.outputs.matrix }}
    steps:
      - id: build
        uses: druzsan/build-matrix@v1
        with:
          matrix: |
            os: ubuntu-latest windows-latest macos-latest,
            python-version: 3.8 3.9 3.10
  # Setup python environment and cache installed packages
  setup-python:
    needs: build-matrix
    strategy:
      matrix: ${{ fromJson(needs.build-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
          cache: pip
      - run: python -m pip install -r requirements.txt
  # Check code quality
  check-code:
    needs: [build-matrix, setup-python]
    strategy:
      matrix: ${{ fromJson(needs.build-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
          cache: pip
      - run: python -m pip install -r requirements.txt
      - run: black --check .
      - run: pylint .
  # Test code
  unit-test:
    needs: [build-matrix, setup-python]
    strategy:
      matrix: ${{ fromJson(needs.build-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
          cache: pip
      - run: pytest
```

## Examples

## Discussions
