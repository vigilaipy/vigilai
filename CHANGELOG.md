# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.0] - 2026-06-13
### Added
- Multi-provider token counting (OpenAI, Anthropic, Groq/generic 
  models) with auto-detection from model name
- Expanded cost tracking with pricing table for major models, 
  plus estimate_cost() method
- Spend guard kill switch via BudgetExceededError and 
  check_budget() method
- Richer HTML reports with inline SVG cost-per-span bar charts 
  and dark theme matching the vigilai brand
- export() method for dumping traces to JSON or CSV
- Expanded PII detection: phone numbers, credit cards, 
  IP addresses
- Expanded secret detection: Anthropic keys, AWS keys, 
  GitHub tokens, private key headers, high-entropy strings
- Expanded prompt injection detection with confidence scoring 
  and new attack patterns (developer mode, DAN mode, system 
  prompt extraction, delimiter injection)
- New OutputGuard class for scanning LLM outputs (PII, secrets, 
  custom denylist) via guard_output()
- Async support: aretry decorator and AsyncFallbackChain
- LoopGuard.get_summary() for iteration/loop reports
- Automated PyPI publishing via GitHub Actions (OIDC trusted 
  publishing)

### Fixed
- Retry decorator no longer uses timeout_sec as sleep delay; 
  now uses proper exponential backoff (1s, 2s, 4s...) with 
  timeout_sec as actual per-attempt execution timeout

## [v0.1.0] - 2026-06-13
### Added
- Initial release of vigilai (published as vigilaipy on PyPI)
- Core Inspector class - unified entry point
- Observability module: span tracing, token counting 
  (tiktoken), cost tracking, latency stats, HTML reports
- Security module: PII scanner, secret/API key leak scanner, 
  prompt injection scanner
- Reliability module: retry with exponential backoff, 
  fallback chains, infinite loop guard
- MIT License, CI pipeline (black, ruff, mypy, pytest) 
  across Python 3.10/3.11/3.12
