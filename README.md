# 📦 Setup matrix

[![⏱️ Quickstart](https://github.com/druzsan/setup-matrix/actions/workflows/quickstart.yml/badge.svg)](https://github.com/druzsan/setup-matrix/actions/workflows/quickstart.yml) [![🔍 CI](https://github.com/druzsan/setup-matrix/actions/workflows/ci.yml/badge.svg)](https://github.com/druzsan/setup-matrix/actions/workflows/ci.yml) [![🧪 Unit Test](https://github.com/druzsan/setup-matrix/actions/workflows/unit-test.yml/badge.svg)](https://github.com/druzsan/setup-matrix/actions/workflows/unit-test.yml) [![🧪 Integration Test](https://github.com/druzsan/setup-matrix/actions/workflows/integration-test.yml/badge.svg)](https://github.com/druzsan/setup-matrix/actions/workflows/integration-test.yml)

GitHub action to create reusable dynamic job matrices for your workflows.

This action adresses a wide known problem of reusing the same job matrix
multiple times or even generating a matrix on the fly.

The main goal of this action is to be as much compatible with built-in
[GitHub matrices](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
as possible and thus allow you a smooth transition in your workflow.

All given examples can be found as GitHub [workflows](https://github.com/druzsan/setup-matrix/tree/main/.github/workflows) and respective [runs](https://github.com/druzsan/setup-matrix/actions).

## ⏱️ Quickstart

Modified [matrix](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs#expanding-or-adding-matrix-configurations) example.

```yaml
jobs:
  # Setup matrix
  setup-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.setup-matrix.outputs.matrix }}
    steps:
      - id: setup-matrix
        uses: druzsan/setup-matrix@v2.0.0
        with:
          # Use | to preserve valid YAML syntax
          matrix: |
            fruit: [apple, pear]
            animal: [quick red fox, lazy dog]
            include:
              - color: green
              - color: pink
                animal: quick red fox
              - color: brown
                animal: cat
            exclude:
              - fruit: apple
                animal: lazy dog
  # Setup python and print version
  echo:
    needs: setup-matrix
    strategy:
      matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - run: |
          echo "fruit: ${{ matrix.fruit }}, animal: ${{ matrix.fruit }}, color: ${{ matrix.color }}"
```

Workflow [runs](https://github.com/druzsan/setup-matrix/actions/workflows/quickstart.yml).

For more examples, see [advanced usage](#advanced-usage)

## 📥 Inputs

Action has only one required input `matrix`, whose syntax is exactly the same as the built-in matrix provided as string.

Full YAML syntax is supported inside input, so you even can add inline comments which will be ignored during parsing.

Not only syntax validity, but also built-in matrix restrictions (e.g. empty resulting matrix) are checked. Error logs try to give as much infomation on problem as possible.

It is highly recommended to use `|` prefix for multi-line strings:

```yaml
uses: druzsan/setup-matrix@v2.0.0
with:
  matrix: | # Setup matrix with OS and Python version
    os: [ubuntu-latest, windows-latest]
    python-version: [3.8, 3.10, 3.12]
    include:
      - os: windows-latest
        python-version: 3.8  # Only use Python 3.8 for MacOS
    exclude:
      - os: windows-latest
        python-version: 3.12  # Do not use Python 3.12 for Windows
```

Flow YAML syntax is also supported:

```yaml
uses: druzsan/setup-matrix@v2.0.0
with:
  matrix: '{ os: [ubuntu-latest, windows-latest], python-version: [3.8, 3.10, 3.12] }'
```

## 📤 Outputs

Parsed matrix is printed inside the action step as a pretty formated YAML, so you can visually inspect it.

Parsed matrix is also set as `MATRIX` environment variable.

### `matrix`

valid JSON matrix ready to be set as `jobs.<job_id>.outputs` used in
`jobs.<job_id>.strategy`:

```yaml
strategy:
  matrix: ${{ fromJson(needs.<job_id>.outputs.matrix) }}
```

## 💪 Advanced Usage

### ♻️ Reusable Matrix

Sometimes you need to run different jobs on the same set of configurations, e.g.
check code formatting, code types and lint code.

Build matrix:

```yaml
setup-matrix:
  runs-on: ubuntu-latest
  outputs:
    matrix: ${{ steps.setup-matrix.outputs.matrix }}
  steps:
    - id: setup-matrix
      uses: druzsan/setup-matrix@v2.0.0
      with:
        matrix: |
          os: [ubuntu-latest, windows-latest, macos-latest]
          python-version: [3.8, 3.10, 3.12]
```

Reuse matrix:

```yaml
check-format:
  needs: setup-matrix
  strategy:
    matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: python -m pip install -IU pip setuptools wheel
    - run: pip install -IUr requirements.txt -r requirements-dev.txt
    - run: black --check .
typecheck:
  needs: setup-matrix
  strategy:
    matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: python -m pip install -IU pip setuptools wheel
    - run: pip install -IUr requirements.txt -r requirements-dev.txt
    - run: mypy main.py && mypy tests
lint:
  needs: setup-matrix
  strategy:
    matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: python -m pip install -IU pip setuptools wheel
    - run: pip install -IUr requirements.txt -r requirements-dev.txt
    - run: ruff check main.py tests
```

Full [solution](.github/workflows/ci.yml) using the `setup-matrix` action and its [runs](https://github.com/druzsan/setup-matrix/actions/workflows/ci.yml).

[Solution](.github/workflows/ci-builtin.yml) using the built-in matrix and its [runs](https://github.com/druzsan/setup-matrix/actions/workflows/ci-builtin.yml).

### 🌊 Dynamic Matrix

Sometimes you need to run a job on different sets of configurations, depending
on branch, triggering event etc.

Build matrix:

```yaml
setup-matrix:
  runs-on: ubuntu-latest
  outputs:
    matrix: ${{ steps.setup-matrix.outputs.matrix }}
  steps:
    # Setup matrix on a dev branch
    - if: startsWith(github.ref, 'refs/tags/')
      uses: druzsan/setup-matrix@v2.0.0
      with:
        matrix: |
          os: [ubuntu-latest, windows-latest, macos-latest]
          python-version: [3.8, 3.10, 3.12]
    # Setup matrix on the main branch
    - if: github.ref == 'refs/heads/main'
      uses: druzsan/setup-matrix@v2.0.0
      with:
        matrix: |
          os: [ubuntu-latest]
          python-version: [3.8, 3.10, 3.12]
          include:
            - os: windows-latest
              python-version: 3.8
            - os: macos-latest
              python-version: 3.8
    # Setup matrix on a tag
    - if: github.ref != 'refs/heads/main' && !startsWith(github.ref, 'refs/tags/')
      uses: druzsan/setup-matrix@v2.0.0
      with:
        matrix: |
          os: [ubuntu-latest]
          python-version: [3.8]
    # MATRIX environment variable is set by the last executed action
    - id: setup-matrix
      run: echo "matrix=$MATRIX" >> $GITHUB_OUTPUT
```

Use dynamic matrix:

```yaml
unit-test:
  needs: setup-matrix
  strategy:
    matrix: ${{ fromJson(needs.setup-matrix.outputs.matrix) }}
  runs-on: ${{ matrix.os }}
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - run: python -m pip install -IU pip setuptools wheel
    - run: pip install -IUr requirements.txt -r requirements-dev.txt
    - run: python -m pytest
```

Full [solution](.github/workflows/unit-test.yml) using the `setup-matrix` action and its [runs](https://github.com/druzsan/setup-matrix/actions/workflows/unit-test.yml).

[Solution](.github/workflows/unit-test-builtin.yml) using the built-in matrix and its [runs](https://github.com/druzsan/setup-matrix/actions/workflows/unit-test-builtin.yml).

## ℹ️ Limitations

Since the action uses Python and Dockerfile, is is mandatory to run it on an Ubuntu runner.

## ⚠️ Breaking Changes

Version 1 syntax is no longer supported. Update inputs when switching to version 2.
