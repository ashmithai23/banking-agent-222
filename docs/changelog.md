# Changelog

All notable changes to VectraBank are documented in this file.

## [2.1.0] - 2026-10-04
### Added
- Interactive Document Ingestion supporting `.pdf`, `.md`, and `.txt` with instant ChromaDB vectorization.
- Deterministic Banking Tools for Debt-to-Income (DTI), Mortgage Amortization, Compound Growth, and AML checks.
- Dynamic Supervisor Agent Routing for intelligent specialist triage.
- Real-Time Server-Sent Events (SSE) token streaming.
- Benchmark test scenarios and automated runner in `benchmarks/`.

### Fixed
- Resolved Windows `cp1252` charmap encoding errors by forcing UTF-8 stdout/stderr.
- Sanitized multi-agent sequence formatting for Gemini API compatibility.
