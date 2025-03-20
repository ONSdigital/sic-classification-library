# SIC Classification Library

Standard Industrial Classification (SIC) Library, initially developed for Survey Assist API.

## Overview

SIC classification library, utilities used to classify industry code based off of Job Title, Job Description and Organisation Description.

## Features

- SIC Lookup.  A utility that uses a well-known set of SIC mappings of organisation descriptions to SIC classification codes.
- SIC Classification. A RAG approach to classification of SIC using input data, semantic search and LLM.

## Prerequisites

Ensure you have the following installed on your local machine:

- [ ] Python 3.12 (Recommended: use `pyenv` to manage versions)
- [ ] `poetry` (for dependency management)
- [ ] Colima (if running locally with containers)
- [ ] Terraform (for infrastructure management)
- [ ] Google Cloud SDK (`gcloud`) with appropriate permissions

### Local Development Setup

The Makefile defines a set of commonly used commands and workflows.  Where possible use the files defined in the Makefile.

#### Clone the repository

```bash
git clone https://github.com/ONSdigital/sic-classification-library.git
cd sic-classification-library
```

#### Install Dependencies

```bash
poetry install
```

### Run Locally

Placeholder

### GCP Setup

Placeholder

### Code Quality

Code quality and static analysis will be enforced using isort, black, ruff, mypy and pylint. Security checking will be enhanced by running bandit.

To check the code quality, but only report any errors without auto-fix run:

```bash
make check-python-nofix
```

To check the code quality and automatically fix errors where possible run:

```bash
make check-python
```

### Documentation

Documentation is available in the docs folder and can be viewed using mkdocs

```bash
make run-docs
```

### Testing

Pytest is used for testing alongside pytest-cov for coverage testing.  [/tests/conftest.py](/tests/conftest.py) defines config used by the tests.

Unit testing for utility functions is added to the [/tests/tests_utils.py](./tests/tests_utils.py)

```bash
make unit-tests
```

All tests can be run using

```bash
make all-tests
```

### Environment Variables

Placeholder
