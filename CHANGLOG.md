# Changelog

All notable changes to the RMG RIO 4 Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-08

### 🚀 Major: Automatic Reconnection System

#### Added
- **Robust automatic reconnection** with exponential backoff (5s → 5min max)
- **Connection health monitoring** (ping every 30 seconds)
- **Advanced entity state management** (available/unavailable status)
- **Manual reconnection service** `rmg_rio4.reconnect`
- **Material Design Icons** with dynamic state-based switching
- **Comprehensive reconnection documentation** (docs/RECONNECTION.md)
- **Enhanced logging** with visual indicators (✅❌🔄💓)

#### Improved
- **Connection robustness**: Automatically handles all disconnection types
- **User feedback**: Entities marked unavailable during outages
- **Performance**: Fast problem detection (30s max)
- **Maintenance**: Transparent reconnection after Rio 4 reboot

#### Technical Implementation
- Continuous monitoring with `_monitor_connection_health()`
- Intelligent reconnection with `_reconnect_loop()`
- Robust TCP error handling (ConnectionError, BrokenPipeError)
- Smart timeouts on commands (5s) and entities (5min)
- Background task management for seamless operation

### 🎨 Icons and User Interface

#### Added
- **Dynamic MDI icons** for relays and DIO entities
- **Icon customization guide** (docs/ICONS.md)
- **Custom HACS repository icon** (PNG 256x256)
- **Correct firmware version** (1.1.4)

#### Icon Details
- Relays: `mdi:electric-switch` (OFF) / `mdi:electric-switch-closed` (ON)
- DIO: `mdi:toggle-switch-off` (OFF) / `mdi:toggle-switch` (ON)
- State-dependent icon switching for better visual feedback

### 🔧 Services Enhanced

#### Updated
- `rmg_rio4.pulse_relay`: Improved error handling and reconnection support
- `rmg_rio4.reconnect`: New service for manual reconnection

### 📖 Documentation

#### Added
- Complete reconnection system documentation
- Icon customization examples and best practices
- Troubleshooting guide for connection issues
- Performance monitoring guidelines

## [1.0.1] - 2025-10-07

### Changed
- **BREAKING**: Removed relay count configuration option from setup flow
- RMG Rio 4 hardware specification: always 4 relays and 4 DIO (no configuration needed)
- Simplified configuration interface with fewer fields
- Hardcoded relay and DIO counts to match hardware specification

### Removed
- Configuration field for "Number of relays" (unnecessary for Rio 4)
- Test scripts and demo files from repository (cleaner production release)
- Developer documentation (moved to separate branch if needed)
- Example automation files (users should create their own)

### Fixed
- HACS compatibility issues resolved
- Repository structure optimized for production use
- Cleaner user experience during setup

## [1.0.0] - 2025-10-07

### Added
- Initial integration for RMG RIO 4 relay box
- TCP communication on port 22023 with proper authentication protocol
- Configuration flow for easy setup via Home Assistant UI
- Support for 4 relays with ON/OFF/PULSE commands
- Real-time state monitoring via push notifications from server
- Service `rmg_rio4.pulse_relay` for temporary relay activation
- Support for Digital I/O monitoring (4 DIO channels)
- Automatic detection of DI (Digital Input) vs DO (Digital Output)
- Multi-language support (French/English translations)
- Comprehensive test scripts for connection validation
- Automatic reconnection on connection loss
- Device information display (serial number, firmware version, hostname)
- HACS (Home Assistant Community Store) compatibility

### Technical Details
- Tested with RMG Rio 4 hardware (S/N: 1000000097badc1a, Firmware: v1.1.4)
- Full protocol implementation matching server specification
- Proper handling of LOGINREQUEST/AUTHENTICATION sequence
- Support for all relay commands: ON, OFF, PULSE with duration
- Real-time monitoring of state changes with push notifications
- Error handling for DI (read-only) vs DO (controllable) digital I/O
- Comprehensive logging and debugging support

### Files Structure
```
custom_components/rmg_rio4/
├── __init__.py          # Main TCP communication logic
├── config_flow.py       # Home Assistant configuration flow
├── switch.py            # Relay and DIO entities
├── services.yaml        # PULSE service definition
├── strings.json         # UI strings
├── manifest.json        # Integration metadata
└── translations/        # Multi-language support
    ├── fr.json
    └── en.json
```

### Supported Commands
- `RELAY1 ON` / `RELAY1 OFF` - Basic relay control
- `RELAY1 PULSE 2.5` - Temporary activation (2.5 seconds)
- `RELAY1?` - Query relay state
- `DIO1?` - Query digital I/O state
- `SERIALNUMBER?` / `FIRMWAREVERSION?` / `HOSTNAME?` - System info

### Home Assistant Entities
- `switch.relais_1` to `switch.relais_4` (controllable relays)
- `switch.dio_1` to `switch.dio_4` (digital inputs, read-only)
- Service: `rmg_rio4.pulse_relay` for timed relay activation

## [Unreleased]

### Planned
- Support for multiple RMG Rio 4 devices
- Enhanced diagnostics and health monitoring
- Additional relay control modes
- Integration with Home Assistant device registry