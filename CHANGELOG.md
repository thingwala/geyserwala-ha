# Change Log - Geyserwala Connect - Home Assistant Integration

## [Unreleased]

### Added
- Timers: per timer a summary sensor, start and end `time` entities, a target temperature `number`, and day-of-week switches (disabled by default). Read every 60 seconds with a separate coordinator; the integration still loads if timers can't be read, and reloads itself when timers are added or deleted.

### Fixed
- Config flow errors showed raw translation keys (e.g. `[%key:common::config_flow::error::cannot_connect%]`).
- When the Geyserwala is rediscovered at a new IP address, the saved host is now updated (it was saved under `ip_address`, which the integration doesn't read), so the device reconnects instead of going unavailable.
- Config flow errors are cleared on a new attempt.

### Changed
- Replace deprecated `async_timeout`, `FlowResult` and `helpers.entity.DeviceInfo` with their current equivalents.

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
