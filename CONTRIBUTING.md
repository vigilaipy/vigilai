# Contributing to vigilai

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Development Setup

1. Fork the repo and clone it locally.
2. Install dependencies:
   ```bash
   pip install -e ".[full]"
   pip install pytest pytest-asyncio black ruff mypy
   ```
3. Run tests before submitting a PR:
   ```bash
   pytest
   black .
   ruff check .
   mypy vigilai
   ```

## Pull Requests

1. Create a new branch.
2. Make your changes and commit them with descriptive messages.
3. Push to your fork and submit a pull request.
4. Ensure all CI checks pass.
