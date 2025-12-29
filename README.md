# Warmlink Heat Pump Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.6.0-blue.svg)](https://github.com/warsztatroch-droid/warmlink-ha/releases)

Custom integration for Phinx/Warmlink heat pumps connected via cloud.linked-go.com.

## Features

- **Climate entity** - Control heating/cooling modes and target temperature
- **Water heater entity** - Control hot water tank
- **550+ entities** - Complete Modbus parameter coverage 🆕
- **Temperature sensors** - T01-T55 (inlet, outlet, ambient, tank, coil, EVI, etc.)
- **Energy sensors** - Power input, heat output, COP/EER
- **Setpoint controls** - R01-R70 with sliders (DHW, heating, cooling, room, zones)
- **Switch controls** - Power, Silent Mode, Cooling, Disinfection, etc.
- **Select controls** - Operating Mode, Control Mode, Temperature unit, etc.
- **Parameter code prefixes** - Entity names show code: `[R01] DHW Target Temperature` 🆕
- **Multi-language** - Polish and English sensor names

## Entity Examples

```
[T01] Inlet Water Temperature     - Temperatura wody wlotowej
[T02] Outlet Water Temperature    - Temperatura wody wylotowej
[T04] Ambient Temperature         - Temperatura zewnętrzna
[R01] DHW Target Temperature      - Temperatura zadana CWU
[R02] Heating Target Temperature  - Temperatura zadana ogrzewania
[G05] Disinfection Enable         - Włączenie dezynfekcji
[H07] Control Mode                - Tryb sterowania
```

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots menu (⋮) → "Custom repositories"
4. Add URL: `https://github.com/warsztatroch-droid/warmlink-ha`
5. Select category: "Integration"
6. Click "Add"
7. Find "Warmlink Heat Pump" and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Copy `custom_components/warmlink` folder to your Home Assistant `/config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "Warmlink"
3. Enter your Warmlink app email and password
4. Select which devices to add
5. Your heat pump entities will be automatically created

## Supported Devices

This integration works with heat pumps using the Warmlink mobile app, including:

- Phinx heat pumps
- Kaisai heat pumps (Warmlink version)
- Other rebranded Warmlink-compatible devices

## API Information

- **API Endpoint**: `cloud.linked-go.com:449`
- **App ID**: 16 (Warmlink)
- Based on reverse engineering of the Warmlink Android app

## Protocol Codes (v1.6.0)

### Temperature Sensors (Read-only)

| Code | Description              | Unit  |
| ---- | ------------------------ | ----- |
| T01  | Inlet Water Temperature  | °C    |
| T02  | Outlet Water Temperature | °C    |
| T03  | Coil Temperature         | °C    |
| T04  | Ambient Temperature      | °C    |
| T05  | Suction Temperature      | °C    |
| T08  | DHW Tank Temperature     | °C    |
| T09  | Room Temperature         | °C    |
| T30  | Compressor Frequency     | Hz    |
| T39  | Water Flow Rate          | L/min |

### Setpoint Controls (Read-Write)

| Code | Description         | Range   |
| ---- | ------------------- | ------- |
| R01  | DHW Target Temp     | 15-70°C |
| R02  | Heating Target Temp | 15-75°C |
| R03  | Cooling Target Temp | 9-28°C  |
| R70  | Room Target Temp    | 5-27°C  |

### Switch Controls

| Code  | Description             |
| ----- | ----------------------- |
| Power | Main power on/off       |
| H01   | Power-off Memory        |
| H05   | Enable Cooling Function |
| H22   | Silent Mode             |
| G05   | Disinfection Enable     |

### Select Controls

| Code | Description      | Options                   |
| ---- | ---------------- | ------------------------- |
| Mode | Operating Mode   | Heating/Cooling/Hot Water |
| H07  | Control Mode     | Display / Remote          |
| H21  | Temperature Unit | Celsius / Fahrenheit      |
| H25  | Temp Control     | Outlet / Room / Buffer    |

## Dashboard

Example dashboards are available in `examples/` folder.

### Option 1: Auto-entities (Recommended)

Uses `auto-entities` card to **automatically detect all Warmlink entities** - no manual DEVICE_CODE needed!

1. Install [auto-entities](https://github.com/thomasloven/lovelace-auto-entities) via HACS:
   - HACS → Frontend → Search "auto-entities" → Install → Restart HA
2. Copy `examples/dashboard_auto.yaml` content to your dashboard
3. Done! All Warmlink entities are detected automatically.

### Option 2: Generate with Script

Generate dashboard with your specific DEVICE_CODE:

```bash
cd examples/
python3 generate_dashboard.py YOUR_DEVICE_CODE
# Creates: dashboard_YOUR_DEVICE_CODE.yaml
```

Find your DEVICE_CODE:
1. Settings → Devices & Services → Warmlink → click device
2. See entity like `sensor.warmlink_abc123def_t01`
3. Your code is: `abc123def`

### Option 3: Manual Template

Use `examples/dashboard.yaml` and replace all `DEVICE_CODE` with your actual code.

## Troubleshooting

### SSL Certificate Errors

The API on port 449 may have certificate issues. The integration uses SSL verification bypass.

### No Devices Found

Make sure you're using credentials from the Warmlink app (not Aqua Temp). Warmlink requires `appId: 16`.

### Entities Not Showing Values

Some entities only appear if your heat pump model supports them. The integration creates entities for all available parameters.

## Credits

- Based on research from [aquatemp integration](https://github.com/radical-squared/aquatemp)
- Modbus register mapping from Kaisai/Phinx documentation (635 parameters)

## License

MIT License
