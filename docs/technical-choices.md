# Technical Choices & Best Practices

> 🤖 **AI Transparency Notice:** This document was written with AI assistance (Claude by Anthropic). The decisions, requirements and validations are human-driven; the drafting and structuring were AI-assisted. See [AI Transparency](./ai-transparency.md) for details.

This document defines the technology stack, project structure, dependencies and coding standards for the Strava Activity Visibility Checker.

---

## Language & Runtime

**Python 3.13+**

Python was chosen for the following reasons:
- Available natively on Linux and macOS, widely installed on Windows
- Minimal setup for end users (`pip install -r requirements.txt`)
- Strong ecosystem for HTTP clients and API integration
- Excellent testing framework (`pytest`)
- Widely used in the sports/data community, lowering the barrier for contributors

---

## Project Structure

```
/
├── src/
│   ├── main.py        # Entry point and orchestration
│   ├── strava.py      # Strava API client (authentication, data fetching)
│   ├── report.py      # Report generation (Markdown output)
│   └── config.py      # Parameter reading and validation
├── tests/
│   ├── test_strava.py
│   ├── test_report.py
│   └── test_config.py
├── docs/
│   ├── functional-spec.md
│   ├── acceptance-tests.md
│   ├── technical-choices.md
│   ├── design-process.md
│   └── ai-transparency.md
├── .github/
│   └── workflows/
│       ├── ci.yml           # CI pipeline (lint + tests on push)
│       └── execution.yml    # Execution pipeline (scheduled + manual)
├── .env.example       # Example environment variable file (no secrets)
├── .gitignore
├── pyproject.toml     # Project configuration (single config file)
├── requirements.txt   # Runtime dependencies
└── README.md
```

Each source file has a single, clearly defined responsibility. This structure is intentionally simple and easy to navigate for any contributor.

---

## Dependencies

### Runtime

| Package | Purpose |
|---------|---------|
| `requests` | HTTP client for Strava API calls |
| `python-dotenv` | Load environment variables from a `.env` file in local development |

### Development & Testing

| Package | Purpose |
|---------|---------|
| `pytest` | Unit test framework |
| `pytest-cov` | Test coverage reporting |
| `ruff` | Linting and formatting (replaces flake8 + black) |
| `responses` | Mock HTTP responses in unit tests (no real API calls) |

---

## Configuration File

A single `pyproject.toml` at the root of the project centralises all tool configuration:
- Project metadata (name, version, Python version requirement)
- `ruff` linting and formatting rules
- `pytest` configuration (test directory, coverage settings)

---

## Coding Standards

The guiding principle is **simplicity and readability**. The code must be easy to understand for any Python developer, regardless of their experience level.

### Type Hints

All functions use Python native type hints. This improves readability and IDE support without adding any runtime overhead.

```python
def is_inconsistent(visibility: str, has_pr: bool) -> bool:
    ...
```

### Linting & Formatting

**Ruff** is used for both linting and formatting. It is the modern Python standard, significantly faster than the traditional flake8 + black combination, and configured via `pyproject.toml`.

The following rules are enforced:
- Standard PEP 8 style
- No unused imports or variables
- Consistent string quotes
- Maximum line length: 100 characters

### Environment Variables

All configuration is passed via environment variables. In local development, a `.env` file is used (loaded automatically by `python-dotenv`). An `.env.example` file is provided in the repository with all required variables listed but no values.

The `.env` file is listed in `.gitignore` and must never be committed.

### Error Handling

- All errors produce a clear, human-readable message on stderr
- The script exits with a non-zero exit code on any unrecoverable error
- Strava API errors are caught and handled explicitly (see functional specification)

---

## Testing

### Framework

**pytest** is the standard Python testing framework. Tests are located in the `tests/` directory, mirroring the `src/` structure.

### Mocking

The `responses` library is used to mock all HTTP calls to the Strava API. Unit tests never make real network requests.

### Coverage

A minimum test coverage of **80%** is enforced. Coverage is measured on every CI run via `pytest-cov`.

### Running Tests Locally

```bash
pytest --cov=src tests/
```

---

## Local Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd strava-visibility-checker

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the example env file and fill in your credentials
cp .env.example .env

# Run the script
python src/main.py

# Run the tests
pytest --cov=src tests/

# Run the linter
ruff check src/ tests/
```

---

## Security

- Strava credentials (`STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, `STRAVA_REFRESH_TOKEN`) are stored as **GitHub Actions secrets** and never committed to the repository
- The `.env` file is excluded from version control via `.gitignore`
- The generated report must never contain credential values (enforced by acceptance test AT-06-2)
- Dependabot vulnerability alerts are enabled on the GitHub repository (default for public repos)

---

## GitHub Actions Pipelines

Two separate workflows are defined:

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| CI | `.github/workflows/ci.yml` | Every push / pull request | Lint + unit tests |
| Execution | `.github/workflows/execution.yml` | Scheduled (monthly) + manual | Run the script, expose report as artifact |

Details of each pipeline are defined in Step 6 and Step 9 of the [design process](./design-process.md).