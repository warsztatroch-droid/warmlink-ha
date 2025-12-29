# Warmlink Heat Pump Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/badge/version-1.8.2-blue.svg)](https://github.com/warsztatroch-droid/warmlink-ha/releases)

Custom integration for Phinx/Warmlink heat pumps connected via cloud.linked-go.com.

## Features

- **Climate entity** - Control heating/cooling modes and target temperature (`Pompa ciepła`)
- **Water heater entity** - Control hot water tank (`Zasobnik CWU`)
- **550+ entities** - Complete Modbus parameter coverage
- **Temperature sensors** - T01-T55 (inlet, outlet, ambient, tank, coil, EVI, etc.)
- **Energy sensors** - Power input, heat output, COP/EER, ODU consumption/generation
- **Zone sensors** - Zone 1/2 room temp, mixing temp, mixing valve
- **Indoor climate** - Indoor temperature (DP4), humidity (DP5), dew point (DP6)
- **Setpoint controls** - R01-R70 with sliders (DHW, heating, cooling, room, zones)
- **Switch controls** - Power, Silent Mode, Cooling, Disinfection, etc.
- **Select controls** - Operating Mode, Control Mode, Temperature unit, etc.
- **Protocol code prefixes** - Entity names include codes: `(T02) Temperatura wody wylotowej`
- **Polish UI** - All entity names, options and labels in Polish 🇵🇱
- **Example dashboards** - Ready-to-use dashboards grouped by protocol codes

## Entity Examples (v1.8.x)

| Nazwa polska (prefix format)      | English Name             |
| --------------------------------- | ------------------------ |
| (T02) Temperatura wody wylotowej  | Outlet Water Temperature |
| (T04) Temperatura zewnętrzna      | Ambient Temperature      |
| (R01) Temperatura zadana CWU      | DHW Target Temperature   |
| (T30) Częstotliwość sprężarki     | Compressor Frequency     |
| (Power In ODU) Pobór mocy ODU     | ODU Power Input          |
| (Zone 1 Room Temp) Strefa 1 temp. | Zone 1 Room Temperature  |
| (DP4) Temperatura wewnętrzna      | Indoor Temperature       |
| (G05) Dezynfekcja                 | Disinfection             |
| (H20) CWU - ZAŁ/WYŁ               | Hot Water ON/OFF         |
| (Mode) Tryb pracy                 | Operating Mode           |

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

## Protocol Codes (v1.8.x)

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
| T12  | Discharge Temperature    | °C    |
| T30  | Compressor Frequency     | Hz    |
| T32  | Max Compressor Frequency | Hz    |
| T39  | Water Flow Rate          | L/min |
| T55  | Outlet Temp After Heater | °C    |

### Energy & Power Sensors (Read-only)

| Code                | Description              | Unit |
| ------------------- | ------------------------ | ---- |
| Power In(Total)     | Total Power Input        | kW   |
| Capacity Out(Total) | Total Heat Output        | kW   |
| COP/EER(Total)      | Efficiency Coefficient   | -    |
| Power In(ODU)       | ODU Power Input          | kW   |
| Capacity Out(ODU)   | ODU Heat Output          | kW   |
| Heating Con.(ODU)   | Heating Energy Consumed  | kWh  |
| Heating Gen.(ODU)   | Heating Energy Generated | kWh  |
| Cooling Con.(ODU)   | Cooling Energy Consumed  | kWh  |
| Cooling Gen.(ODU)   | Cooling Energy Generated | kWh  |
| DHW Con.(ODU)       | DHW Energy Consumed      | kWh  |
| DHW Gen.(ODU)       | DHW Energy Generated     | kWh  |

### Zone & Indoor Sensors (Read-only)

| Code                | Description           | Unit |
| ------------------- | --------------------- | ---- |
| Zone 1 Room Temp    | Zone 1 Room Temp      | °C   |
| Zone 2 Room Temp    | Zone 2 Room Temp      | °C   |
| Zone 2 Mixing Temp  | Zone 2 Mixing Temp    | °C   |
| Zone 2 Mixing Valve | Zone 2 Mixing Valve   | %    |
| DP4                 | Indoor Temperature    | °C   |
| DP5                 | Indoor Humidity       | %    |
| DP6                 | Dew Point Temperature | °C   |

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

Example dashboards are available in `examples/` folder:

| Plik                                         | Opis                                                                              |
| -------------------------------------------- | --------------------------------------------------------------------------------- |
| `dashboard_auto.yaml`                        | Automatyczne wykrywanie encji (wymaga auto-entities)                              |
| `dashboard_0c7fedc122c1_grupy.yaml`          | **Dashboard pogrupowany wg kodów protokołu (T, R, A, C, D, E, F, G, H, O, P, Z)** |
| `dashboard_0c7fedc122c1_kategoryzowany.yaml` | Dashboard pogrupowany funkcjonalnie                                               |
| `dashboard.yaml`                             | Szablon z DEVICE_CODE do zamiany                                                  |

### Dashboard pogrupowany wg kodów (Recommended)

Plik `dashboard_0c7fedc122c1_grupy.yaml` zawiera 14 zakładek:

| Zakładka         | Ikona              | Opis                                          |
| ---------------- | ------------------ | --------------------------------------------- |
| Przegląd         | 🔥 heat-pump       | Główne sterowanie, status, wydajność          |
| T - Temperatury  | 🌡️ thermometer     | Wszystkie odczyty temperatur (T01-T55)        |
| R - Setpoints    | 🎯 target          | Temperatury zadane (R01-R70)                  |
| A - Ochrona      | 🛡️ shield-check    | Zabezpieczenia (A03, A04, A06, A11, A26, A29) |
| C - Sprężarka    | ⚙️ cog-sync        | Częstotliwość sprężarki (C01-C06)             |
| D - Odszranianie | ❄️ snowflake-melt  | Cykl odszraniania (D01-D26)                   |
| E - EEV          | 🔧 valve           | Zawór rozprężny (E01-E03)                     |
| F - Wentylator   | 🌀 fan             | Silnik wentylatora (F01-F23)                  |
| G - Dezynfekcja  | 🦠 shield-bug      | Anti-Legionella (G01-G05)                     |
| H - Konfiguracja | ⚙️ cog             | System (H01-H37)                              |
| O - Wyjścia      | 🔌 electric-switch | Outputs (O01-O04)                             |
| P - Pompa        | 💧 pump            | Pompa obiegowa (P01-P03)                      |
| Z - Strefy       | 🏠 home-floor-1    | Sterowanie strefowe (Z17)                     |
| Energia          | ⚡ lightning-bolt  | COP, zużycie energii                          |
| Info             | ℹ️ information     | Wersje firmware                               |

Użycie:

1. Skopiuj zawartość pliku do dashboardu w HA
2. Zamień `0c7fedc122c1` na kod swojego urządzenia

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

## Changelog

### v1.8.2 (2024-12-29)
- 🇵🇱 All binary_sensor names in Polish (Online, Power, Fault → Status połączenia, Status zasilania, Status awarii)

### v1.8.1 (2024-12-29)
- 🇵🇱 Fixed H20 options to Polish (CWU - ZAŁ/WYŁ)
- 🇵🇱 Fixed water_heater name to "Zasobnik CWU"
- 🇵🇱 Fixed climate name to "Pompa ciepła"
- 🇵🇱 Fixed Mode options to Polish (Grzanie, Chłodzenie, CWU, Grzanie+CWU, Chłodzenie+CWU)

### v1.8.0 (2024-12-29)
- ✨ Added protocol code prefixes to all entity names: `(T02) Temperatura wody wylotowej`
- 📊 Prefixes allow better sorting and organization in Home Assistant UI
- 📝 Updated translations (en.json, pl.json)

### v1.7.0 (2024-12-28)
- ✨ 550+ entities with full Modbus parameter coverage
- 🌡️ Temperature sensors T01-T55
- ⚡ Energy sensors (COP, power input/output)
- 🏠 Zone and indoor climate sensors
- 🎚️ Setpoint controls R01-R70

## License

MIT License
