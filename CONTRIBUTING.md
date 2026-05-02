# Contributing to regulasi-id-corpus-prep

Thank you for your interest in contributing! This project aims to make Indonesian regulatory documents more accessible for NLP and legal research.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ziffan/regulasi-id-corpus-prep.git
   cd regulasi-id-corpus-prep
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests:**
   ```bash
   pytest
   ```

## Branch Naming Convention

- `feat/`: New features
- `fix/`: Bug fixes
- `docs/`: Documentation changes
- `refactor/`: Code refactoring
- `test/`: Adding or updating tests

## Commit Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat: add ojk-pojk profile`
- `fix: handle empty pages in PDF`
- `docs: update installation guide`

## Pull Request Process

1. Fork the repository.
2. Create a branch for your change.
3. Add tests for any new functionality.
4. Ensure all tests pass.
5. Submit a PR to the `main` branch.
6. A maintainer will review your PR.

## Developer Certificate of Origin (DCO)

To ensure that all contributions are legally cleared for open-source distribution, we require all commits to be signed off. Use `git commit -s` to add the `Signed-off-by` line to your commit message.

## Coding Standards

- We use `ruff` for linting and formatting.
- Ensure your code adheres to the project's existing style.

## Testing Requirement

Every new feature or bug fix must include corresponding tests. We aim for high test coverage to maintain stability.
