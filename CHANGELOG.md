<!-- markdownlint-disable MD024 -->
# Change Log - Geyserwala Connect - Home Assistant Integration

## [0.1.0] - 2026-05-17

### Added
- Integration options flow for configurable update interval.
- Shared platform setup helper to reduce cross-module coupling.
- Initial unit tests for setup and entity helper behavior.
- CI workflow for `ruff` and `pytest`.

### Changed
- Coordinator update logic hardened with timeout handling, bounded retries, and clearer error propagation.
- Improved platform entity setup reliability and icon fallback behavior.
- Added support for YAML custom `text` entities in config schema.
- Improved typing and maintainability across core modules.

### Docs
- Expanded README with polling options, reliability details, troubleshooting, and development workflow.

## [0.0.9] - 2025-04-30

### Changed
- Entity IDs are derived from the device hostname, previously the device name.

## [0.0.8] - 2023-12-22

Allow for custom values.

## [0.0.7] - 2023-12-09

Migrate to persistent latch signals, with programmable hold time

### Added
- `external-disable` signal: accepts integer of number of seconds to latch, or true (defaults to 24 hours). Zero/false will clear.

### Changed
- `external-demand` signal: accepts integer of number of seconds to latch, or true (defaults to 24 hours). Zero/false will clear.

### Removed
- `lowpower-enable`: replaced by `external-disable`.

## [0.0.6] - 2023-08-08

Initial development
