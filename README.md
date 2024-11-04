# Python Code Coverage Analyzer

![Python Version](https://img.shields.io/badge/python-3.13-blue)
![Test Workflow](https://github.com/martineberlein/coveragetracer/actions/workflows/tests.yaml/badge.svg)
[![License](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python tool to analyze code coverage and extract detailed insights into code blocks (optional). Primarily, it helps analyze the coverage of a Python project, with optional AST-based code block analysis for deeper code understanding.

## Usage

### Coverage Analysis with CoverageAnalyzer

The CoverageAnalyzer provides a flexible way to analyze code coverage by running specified tests on a project. Initialize CoveragePyAnalyzer with the project root and, optionally, a test harness.

Example usage:

```python
from coverageanalyzer.line import CoveragePyAnalyzer
from pathlib import Path

analyzer = CoveragePyAnalyzer(
    project_root=Path("resources/project"),
    harness=Path("resources/harness.py")
)

# Run coverage analysis with a set of tests
report = analyzer.get_coverage(tests=["sqrt(12)", "sin(10)", "tan(10)"])
print("Coverage Report:", report)
print(f"Total Coverage: {report.get_total_coverage() * 100:.2f}%")
```

#### Incremental Coverage Analysis

With CoveragePyAnalyzer, you can append new tests to accumulate coverage incrementally without clearing previous results. For example:

```python
# Start fresh coverage analysis
analyzer.reset()

# Incrementally add tests
initial_tests = ["sqrt(16)", "cos(1)"]
for test in initial_tests:
    report = analyzer.append_coverage(test)
    print(f"Coverage after '{test}': {report.get_total_coverage() * 100:.2f}%")
```

This flexible approach allows you to track coverage on a per-test basis.

### Code Block Analysis with CodeBlockAnalyzer

The BlockAnalyzer provides an optional feature for identifying specific code blocks in Python files. This can be useful for examining code structure or targeted refactoring.

Example usage:

```python
from coverageanalyzer.block import BlockCoveragePyAnalyzer
from pathlib import Path

# Initialize the analyzer for a specific project directory
block_analyzer = BlockCoveragePyAnalyzer(project_root=Path("resources/project"))

# Access extracted code blocks
for file, blocks in block_analyzer.file_blocks.items():
    print(f"File: {file}")
    for block in blocks:
        print(block)
```

## Features

- **Coverage Analysis**: Uses `coverage.py` to assess code coverage at the function and file level.
- **Flexible Test Execution**: Supports re-running coverage analysis with different test sets.
- **Optional Code Block Analysis**: Uses AST parsing to extract specific code blocks (e.g., functions, classes) from Python files within a specified directory.

## Installation

### Prerequisites

- Python 3.10 or higher

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/martineberlein/coveragetracer.git
   cd coveragetracer
   ```

2. Install the package:
   ```bash
   pip install .
   ```
