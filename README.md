# vigilai

![PyPI version](https://img.shields.io/pypi/v/vigilai.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![CI Status](https://github.com/vigilai/vigilai/actions/workflows/ci.yml/badge.svg)

**A developer-first AI observability, security, and reliability toolkit for LLM applications and AI agents.** Think of it as the scikit-learn of AI safety.

## Installation

You can install `vigilai` via pip. Choose the installation that fits your needs:

```bash
# Core features (observability & reliability)
pip install vigilai

# Include security scanning (PII, secrets, injection detection)
pip install "vigilai[security]"

# Full installation
pip install "vigilai[full]"
```

## Quick Start

```python
from vigilai import Inspector

ins = Inspector(model="gpt-4o", provider="openai")

with ins.trace("my_run"):
    # Your LLM logic here
    print("Doing some AI stuff...")

ins.stats()
```

## Features

| Module          | Description                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| **Observability**| Tracing spans, token counting, cost tracking, local JSONL structured logging.|
| **Security**     | Detect PII, secrets, and prompt injections via `ins.scan()`.                  |
| **Reliability**  | Automatic retry with backoff, fallback chains, and infinite loop guards.      |

## Documentation

For full documentation, see our [Docs](docs/index.md).
