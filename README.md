# Setup matrix

GitHub action to create reusable dynamic job matrices for your workflows.

This action adresses a wide known problem of reusing the same job matrix
multiple times or even generating a matrix on the fly.

The main goal of this action is to be as much compatible with built-in
[GitHub matrices](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
as possible and thus allow you a smooth transition in your workflow.

All given examples can be found as GitHub workflows in
[this repository](https://github.com/druzsan/test-setup-matrix).

## Basic usage

```yaml
jobs:
  # Setup matrix
  setup-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.setup-matrix.outputs.matrix }}
    steps:
      - id: setup-matrix
        uses: druzsan/setup-matrix@v1
        with:
          matrix: |
            os: ubuntu-latest windows-latest macos-latest,
            python-version: 3.8 3.9 3.10
  # Setup python and print version
  setup-python:
    needs: setup-matrix
    strategy:
      matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
      - run: python --version
```

For more examples, see [advanced usage](#advanced-usage)

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
other characters are allowed, but valid behaviour cannot be validated for all
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

Optioal extra matrix configurations to add to the base matrix. Must have the
following syntax:

```
variable-i: value variable-j: value <...>,
                   <...>
variable-k: value variable-l: value <...>[,]
```

Variable names in each "row" should be unique but can differ from the ones in
the [`matrix`](#matrix) input.

### `exclude`

Optional matrix configurations to exclude from the base matrix. Have the same
syntax and restrictions as [`include`](#include).

## Outputs

Parsed matrix is printed inside the action's step as a pretty formated YAML
using `yq`, so you can visually inspect it.

Parsed matrix is also set as `MATRIX` environment variable.

### `matrix`

valid JSON matrix ready to be set as `jobs.<job_id>.outputs` used in
`jobs.<job_id>.strategy`:

```yaml
matrix: ${{ fromJson(needs.<job_id>.outputs.matrix) }}
```

## Errors

Not only syntax validity, but also built-in matrix' restrictions are checked. If
you find a case where either of the checks does not work, feel free to report as
an issue.

Error logs try to give as much infomation on problem as possible.

## Advanced usage

### Reuse a matrix

Sometimes you need to run different jobs on the same set of configurations, e.g.
install python dependencies, check code quality and run unit tests.

<details>
    <summary>Solution using the built-in matrix</summary>

```yaml
jobs:
  # No matrix setup
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
      - run: mypy .
      - run: pylint src
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
      - run: python -m pip install -r requirements.txt
      - run: python -m pytest
```

</details>

```yaml
jobs:
  # Setup matrix
  setup-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.setup-matrix.outputs.matrix }}
    steps:
      - id: setup-matrix
        uses: druzsan/setup-matrix@v1
        with:
          matrix: |
            os: ubuntu-latest windows-latest macos-latest,
            python-version: 3.8 3.9 3.10
  # Setup python environment and cache installed packages
  setup-python:
    needs: setup-matrix
    strategy:
      matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
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
    needs: [setup-matrix, setup-python]
    strategy:
      matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
          cache: pip
      - run: python -m pip install -r requirements.txt
      - run: black --check .
      - run: mypy .
      - run: pylint src
  # Test code
  unit-test:
    needs: [setup-matrix, setup-python]
    strategy:
      matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
          cache: pip
      - run: python -m pip install -r requirements.txt
      - run: python -m pytest
```

### Setup dynamic matrix

Sometimes you need to run a job on different sets of configurations, depending
on branch, triggering event etc.

<details>
    <summary>Solution using the built-in matrix</summary>

```yaml
jobs:
  # No matrix setup
  # Test code on a dev branch
  unit-test-dev:
    if: github.ref != 'refs/heads/main' && !startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - run: python -m pip install -r requirements.txt
      - run: python -m pytest
  # Test code on the main branch
  unit-test-main:
    if: github.ref == 'refs/heads/main'
    strategy:
      matrix:
        os: [ubuntu-latest]
        python-version: ['3.8', '3.9', '3.10']
        include:
          - os: windows-latest
            python-version: '3.8'
          - os: macos-latest
            python-version: '3.8'
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
      - run: python -m pip install -r requirements.txt
      - run: python -m pytest
  # Test code on a tag
  unit-test-tag:
    if: startsWith(github.ref, 'refs/tags/v')
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
      - run: python -m pip install -r requirements.txt
      - run: python -m pytest
```

</details>

```yaml
jobs:
  # Setup matrix
  setup-matrix:
    runs-on: ubuntu-latest
    steps:
      - if: startsWith(github.ref, 'refs/tags/v')
        uses: druzsan/setup-matrix@v1
        with:
          matrix: |
            os: ubuntu-latest windows-latest macos-latest,
            python-version: 3.8 3.9 3.10
      - if: github.ref == 'refs/heads/main'
        uses: druzsan/setup-matrix@v1
        with:
          matrix: |
            os: ubuntu-latest,
            python-version: 3.8 3.9 3.10
          include: |
            os: windows-latest python-version: 3.8,
            os: macos-latest python-version: 3.8
      - if: github.ref != 'refs/heads/main' && !startsWith(github.ref, 'refs/tags/v')
        uses: druzsan/setup-matrix@v1
        with:
          matrix: |
            os: ubuntu-latest,
            python-version: 3.8
      # MATRIX environment variable is set by the last executed action
      - id: set-matrix
        run: echo "matrix=$MATRIX" >> $GITHUB_OUTPUT
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
  # Test code
  unit-test:
    needs: setup-matrix
    strategy:
      matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '${{ matrix.python-version }}'
      - run: python -m pip install -r requirements.txt
      - run: python -m pytest
```

## Limitations

[Parsing](./parse-matrix.sh) the input is written in bash using sed, grep and
jq, so running on an Ubuntu runner is mandatory.

There is currently no way to pass multiline strings or strings containing colons
and/or commas as variable names or values. If you need to have such strings
please open an issue.
