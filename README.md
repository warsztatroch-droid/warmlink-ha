# Warmlink Heat Pump Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Custom integration for Phinx/Warmlink heat pumps connected via cloud.linked-go.com.

## Features

- **Climate entity** - Control heating/cooling modes and target temperature
- **Water heater entity** - Control hot water tank
- **Temperature sensors** - Inlet (T01), Outlet (T02), Ambient (T03), Tank (T04), Coil (T05)
- **Setpoint sensors** - Water (R01), Room (R02), Cooling (R03)
- **Binary sensors** - Online status, Power state, Fault detection
- **Number controls** - Setpoint sliders for DHW, heating, cooling, room, zones 🆕
- **Switch controls** - Power, Silent Mode, Cooling Mode, Disinfection 🆕
- **Select controls** - Operating Mode, Control Mode, Temperature unit 🆕
- **Shared devices support** - Access devices shared with you from other accounts 👥
- **Multi-language** - Polish and English sensor names

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
4. Your heat pump devices will be automatically discovered

## Supported Devices

This integration works with heat pumps using the Warmlink mobile app, including:

- Phinx heat pumps
- Kaisai heat pumps (Warmlink version)
- Other rebranded Warmlink-compatible devices

## API Information

- **API Endpoint**: `cloud.linked-go.com:449`
- **App ID**: 16 (Warmlink)
- Based on reverse engineering of the Warmlink Android app

## Protocol Codes

The integration reads the following data from your heat pump:

| Code  | Description                                |
| ----- | ------------------------------------------ |
| Power | On/Off state                               |
| Mode  | Operating mode (Heating/Cooling/Hot Water) |
| T01   | Inlet water temperature                    |
| T02   | Outlet water temperature                   |
| T03   | Ambient temperature                        |
| T04   | Tank temperature                           |
| T05   | Coil temperature                           |
| R01   | Water setpoint                             |
| R02   | Room setpoint                              |
| R03   | Cooling setpoint                           |

## Control Entities (v1.4.0+)

### Number Controls (Setpoints)

| Entity         | Description                | Range      |
| -------------- | -------------------------- | ---------- |
| R01 DHW Target | Hot water tank temperature | 15-70°C    |
| R02 Heating    | Heating setpoint           | 15-75°C    |
| R03 Cooling    | Cooling setpoint           | 9-28°C     |
| R70 Room       | Room temperature setpoint  | 5-27°C     |
| Zone 1-3 Temps | Multi-zone control         | 15-60°C    |
| Fan Speeds     | F18-F26 fan parameters     | 0-1000 RPM |

### Switch Controls

| Entity       | Code | Description                   |
| ------------ | ---- | ----------------------------- |
| Power        | -    | Main power on/off             |
| Silent Mode  | H22  | Reduce noise (lower fan)      |
| Cooling Mode | H05  | Enable cooling function       |
| Disinfection | G05  | Anti-legionella (manual)      |
| Power Memory | H01  | Restore state after power cut |

### Select Controls

| Entity       | Code | Options                            |
| ------------ | ---- | ---------------------------------- |
| Mode         | Mode | Heating/Cooling/Hot Water/Combined |
| Control Mode | H07  | Outlet temp / Delta T / Room temp  |
| Temp Unit    | H21  | Celsius / Fahrenheit               |
| Temp Control | H25  | Outlet / Room / Ext thermostat     |
| EVI Function | H27  | Enable enhanced vapor injection    |
| DHW Function | H28  | Quick / Eco / Floor Heating / Zone |

## Troubleshooting

### SSL Certificate Errors

The API on port 449 may have certificate issues. The integration uses SSL verification bypass.

### No Devices Found

Make sure you're using credentials from the Warmlink app (not Aqua Temp). Warmlink requires `appId: 16`.

### Shared Devices Not Visible

If someone shared a device with you through the Warmlink app, the integration will automatically fetch it using the `getAuthDeviceList` API. Shared devices are marked with 👥 icon during setup.

## Credits

- Based on research from [aquatemp integration](https://github.com/radical-squared/aquatemp)
- Modbus register mapping from Kaisai/Phinx documentation

## License

MIT License
