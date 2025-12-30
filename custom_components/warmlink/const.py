"""Constants for the Warmlink integration."""
from typing import Final

# Import complete Modbus parameters from generated file
from .modbus_params import (
    WRITABLE_PARAMS as MODBUS_WRITABLE_PARAMS,
    SENSOR_PARAMS as MODBUS_SENSOR_PARAMS,
    SWITCH_PARAMS as MODBUS_SWITCH_PARAMS,
    SELECT_PARAMS as MODBUS_SELECT_PARAMS,
)

DOMAIN: Final = "warmlink"
DEFAULT_NAME: Final = "Warmlink"

# Configuration keys
CONF_LANGUAGE: Final = "language"
CONF_DEVICES: Final = "devices"
SUPPORTED_LANGUAGES: Final = ["en", "pl"]

# API Configuration - VERIFIED via API testing
API_BASE_URL: Final = "https://cloud.linked-go.com:449/crmservice/api"
API_TIMEOUT: Final = 30
UPDATE_INTERVAL: Final = 60  # seconds

# Warmlink specific parameters
APP_ID: Final = "16"
LOGIN_SOURCE: Final = "IOS"
AREA_CODE: Final = "en"

# API Endpoints - VERIFIED
ENDPOINT_LOGIN: Final = "app/user/login"
ENDPOINT_USER_INFO: Final = "app/user/getUserInfo"
ENDPOINT_DEVICE_LIST: Final = "app/device/deviceList"
ENDPOINT_DEVICE_STATUS: Final = "app/device/getDeviceStatus"
ENDPOINT_DEVICE_CONTROL: Final = "app/device/control"
ENDPOINT_DEVICE_DATA: Final = "app/device/getDataByCode"
ENDPOINT_DEVICE_FAULT: Final = "app/device/getFaultDataByDeviceCode"
# Shared/authorized devices endpoints (for devices shared with user)
# Try multiple paths as API may use different routes
ENDPOINT_AUTH_DEVICE_LIST: Final = "app/device/getAuthDeviceList"
ENDPOINT_AUTH_DEVICE_LIST_ALT: Final = "device/getAuthDeviceList"

# Warmlink Product ID - VERIFIED
WARMLINK_PRODUCT_ID: Final = "1501438265440362496"

# Device Models (from API custModel field)
DEVICE_MODELS: Final = {
    "PASRW020-BP-PS-D": "Phinx 20kW Heat Pump",
    # More models to be discovered
}

# HVAC Modes - VERIFIED
HVAC_MODE_OFF: Final = "0"
HVAC_MODE_HEATING: Final = "1"
HVAC_MODE_COOLING: Final = "2"
HVAC_MODE_HOT_WATER: Final = "3"
HVAC_MODE_HEATING_HOT_WATER: Final = "4"
HVAC_MODE_COOLING_HOT_WATER: Final = "5"

# Protocol codes - VERIFIED via API testing + Modbus CSV mapping
# =============================================================================
# PROTOCOL CODE CATEGORIES:
# T - Temperature sensors (read-only, Modbus 2xxx)
# R - Setpoints/Target temperatures (read-write, Modbus 1157-1239)
# A - Protection parameters (read-write, Modbus 1037-1058)
# H - System configuration (read-write, Modbus 1018-1041)
# C - Compressor parameters (read-write, Modbus 1218-1223)
# D - Defrost parameters (read-write, Modbus 1105-1126)
# E - EEV (Electronic Expansion Valve) parameters (read-write, Modbus 1131-1138)
# F - Fan parameters (read-write, Modbus 1059-1104)
# G - Disinfection/Anti-legionella (read-write, Modbus 1152-1156)
# P - Pump parameters (read-write, Modbus 1197-1205)
# Z - Zone control (read-write, Modbus 1069-1076)
# O - Outputs/Load status (read-only, Modbus 2018-2022)
# L - Load/Energy Level coordination (read-write, Modbus 5091+) - cascade systems
# DP - Display Panel sensors (read-only, Modbus 2178-2179)
# =============================================================================
PROTOCOL_CODES_STATUS: Final = [
    "Power",        # 0=off, 1=on (Modbus 1011)
    "Mode",         # 0=HotWater, 1=Heating, 2=Cooling, 3=HW+Heating, 4=HW+Cooling (Modbus 1012)
    "ModeState",    # Read-only: 0=Cooling, 1=Heating, 2=Defrost, 3=Disinfection, 4=HotWater (Modbus 2012)
    "Power State",  # Read-only power state (Modbus 2011)
]

# =============================================================================
# T - TEMPERATURE SENSORS (Read-only, Modbus 2042-2077)
# =============================================================================
# Main temperatures
PROTOCOL_CODES_T_TEMPS: Final = [
    "T01",  # Inlet Water Temp (Modbus 2045)
    "T02",  # Outlet Water Temp (Modbus 2046)
    "T03",  # Coil Temp (Modbus 2049)
    "T04",  # Ambient Temp AT (Modbus 2048)
    "T05",  # Suction Temp (Modbus 2051)
    "T06",  # Antifreeze Temp (Modbus 2055)
    "T07",  # Buffer Tank Temp (Modbus 2052)
    "T08",  # DHW Tank Temp (Modbus 2047)
    "T09",  # Room Temp (Modbus 2058)
    "T10",  # EVI Inlet Temp (Modbus 2063)
    "T11",  # EVI Outlet Temp (Modbus 2064)
    "T12",  # Exhaust/Discharge Temp (Modbus 2053)
    "T14",  # Distributor Tube Temp (Modbus 2050)
    "T33",  # IPM Fault Temp
    "T38",  # IPM Module Temp (Modbus 2044)
    "T49",  # Evaporation Temperature (Modbus 2065)
    "T50",  # Exhaust Superheat (Modbus 2066)
    "T51",  # Superheat (Modbus 2067)
    "T55",  # Outlet Temp After Electric Heater (Modbus 2068)
]

# Electrical parameters (also use T prefix)
PROTOCOL_CODES_T_ELECTRICAL: Final = [
    "T15",  # Low Pressure (Modbus 2069) - bar
    "T34",  # AC Input Voltage (Modbus 2062) - V
    "T35",  # AC Input Current (Modbus 2057) - A
    "T36",  # Compressor Phase Current (Modbus 2042) - A
    "T37",  # DC Bus Voltage (Modbus 2043) - V
    "T39",  # Water Flow Rate (Modbus 2077) - L/min
    "T46",  # External Fan Driver IPM Temp
    "T47",  # External Fan Driver Power - kW
    "T48",  # External Fan Driver Current - A
]

# Compressor/Fan frequency and speed (also use T prefix)
PROTOCOL_CODES_T_FREQUENCY: Final = [
    "T27",  # Fan Motor 1 Speed (Modbus 2074) - RPM
    "T28",  # Fan Motor 2 Speed (Modbus 2075) - RPM
    "T29",  # Target Fan Speed (Modbus 2076) - RPM
    "T30",  # Compressor Frequency (Modbus 2071) - Hz
    "T31",  # Compressor Working Frequency (Modbus 2072) - Hz
    "T32",  # Max Compressor Frequency from Driver (Modbus 2073) - Hz
]

# Combined T codes for backward compatibility
PROTOCOL_CODES_TEMPS: Final = (
    PROTOCOL_CODES_T_TEMPS +
    PROTOCOL_CODES_T_ELECTRICAL +
    PROTOCOL_CODES_T_FREQUENCY
)

# =============================================================================
# R - SETPOINTS / TARGET TEMPERATURES (Read-write, Modbus 1157-1239)
# =============================================================================
PROTOCOL_CODES_R_SETPOINTS: Final = [
    "R01",  # DHW Target Temp (Modbus 1157, range R36-R37)
    "R02",  # Heating Target Temp (Modbus 1158, range R10-R11)
    "R03",  # Cooling Target Temp (Modbus 1159, range R08-R09)
    "R04",  # Temp Diff for Power-on Heating (Modbus 1160)
    "R05",  # Temp Diff for Standby Heating (Modbus 1161)
    "R06",  # Temp Diff for Power-on Cooling (Modbus 1174)
    "R07",  # Temp Diff for Standby Cooling (Modbus 1175)
    "R08",  # Min Cooling Target Temp (Modbus 1162)
    "R09",  # Max Cooling Target Temp (Modbus 1163)
    "R10",  # Min Heating Target Temp (Modbus 1164)
    "R11",  # Max Heating Target Temp (Modbus 1165)
    "R16",  # Temp Diff for Power-on DHW (Modbus 1195)
    "R17",  # Temp Diff for Standby DHW (Modbus 1196)
    "R36",  # Min DHW Target Temp (Modbus 1176)
    "R37",  # Max DHW Target Temp (Modbus 1177)
    "R70",  # Target Room Temp (Modbus 1239)
]

# Alias for backward compatibility
PROTOCOL_CODES_SETPOINTS: Final = PROTOCOL_CODES_R_SETPOINTS

# Energy and Performance - from Modbus CSV
PROTOCOL_CODES_ENERGY: Final = [
    "Power In(Total)",      # Total Power Input kW (Modbus 2054)
    "Capacity Out(Total)",  # Total Capacity Output kW (Modbus 2059)
    "COP/EER(Total)",       # COP/EER (Modbus 2060)
    "Comsuption Power",     # Consumption kWh (Modbus 2078+2079)
    "Power In(ODU)",        # ODU Power Input kW (Modbus 2137)
    "Capacity Out(ODU)",    # ODU Capacity Output kW (Modbus 2138)
    "Heating Con.(ODU)",    # Heating Consumption kWh (Modbus 2117+8)
    "Heating Gen.(ODU)",    # Heating Generated kWh (Modbus 2119+8)
    "Cooling Con.(ODU)",    # Cooling Consumption kWh (Modbus 2121+8)
    "Cooling Gen.(ODU)",    # Cooling Generated kWh (Modbus 2123+8)
    "DHW Con.(ODU)",        # DHW Consumption kWh (Modbus 2125+8)
    "DHW Gen.(ODU)",        # DHW Generated kWh (Modbus 2127+8)
]

# Zone and Indoor Climate sensors - from Modbus CSV
PROTOCOL_CODES_CLIMATE: Final = [
    "Zone 1 Room Temp",     # Zone 1 Room Temperature (Modbus 2160)
    "Zone 2 Room Temp",     # Zone 2 Room Temperature (Modbus 2162)
    "Zone 2 Mixing Temp",   # Zone 2 Mixing Temperature (Modbus 2161)
    "Zone 2 Mixing Valve",  # Zone 2 Mixing Valve % (Modbus 2163)
    "DP4",                  # Indoor Temperature (Modbus 2178)
    "DP5",                  # Indoor Humidity (Modbus 2179)
    "DP6",                  # Dew Point Temperature
]

# =============================================================================
# H - SYSTEM CONFIGURATION (Read-write, Modbus 1018-1041)
# =============================================================================
PROTOCOL_CODES_H_CONFIG: Final = [
    "H01",  # Enable Power-off Memory (Modbus 1018)
    "H05",  # Enable Cooling Function (Modbus 1021)
    "H07",  # Control Mode (Modbus 1023)
    "H10",  # Unit Address (Modbus 1024)
    "H18",  # Electric Heater Stage (Modbus 1032)
    "H20",  # 3-way Valve Polarity (Modbus 1033)
    "H21",  # Temperature Unit (Modbus 1029)
    "H22",  # Enable Silent Mode (Modbus 1030)
    "H25",  # Temp Control Selection (Modbus 1035)
    "H27",  # Enable EVI (Modbus 1027)
    "H28",  # Heating/Cooling+DHW Enabled (Modbus 1028)
    "H29",  # Operation Code (Modbus 1034)
    "H30",  # Indoor Unit Type (Modbus 1036)
    "H31",  # Circulation Pump Type (Modbus 1041)
    "H33",  # Fan+Comp Driver Integrated (Modbus 1019)
    "H36",  # Enable Weather Compensation (Modbus 1236)
    "H45",  # Enable Showing COP and Heating Output (Modbus 1404)
]

# Alias for backward compatibility
PROTOCOL_CODES_CONFIG: Final = PROTOCOL_CODES_H_CONFIG

# =============================================================================
# A - PROTECTION PARAMETERS (Read-write, Modbus 1037-1058)
# =============================================================================
PROTOCOL_CODES_A_PROTECTION: Final = [
    "A03",  # Shutdown Ambient Temp (Modbus 1037)
    "A04",  # Antifreeze Temp (Modbus 1038)
    "A05",  # Antifreeze Temp Difference (Modbus 1039)
    "A06",  # Max Exhaust Temp (Modbus 1040)
    "A11",  # Enable Low Pressure Sensor (Modbus 1042)
    "A22",  # Min Antifreeze Temp (Modbus 1053)
    "A23",  # Min Outlet Water Temp Protect (Modbus 1043)
    "A24",  # Excess Temp Diff Inlet/Outlet (Modbus 1044)
    "A26",  # Refrigerant Type (Modbus 1054)
    "A29",  # Enable High Pressure Sensor (Modbus 1058)
    "A31",  # Electric Heater On AT (Modbus 1049)
    "A32",  # Electric Heater Delay Comp On Time (Modbus 1050)
    "A34",  # Crank Preheating Time (Modbus 1064)
    "A35",  # Electric Heater OFF Temp Diff (Modbus 1031)
]

# Alias for backward compatibility
PROTOCOL_CODES_PROTECTION: Final = PROTOCOL_CODES_A_PROTECTION

# =============================================================================
# P - PUMP PARAMETERS (Read-write, Modbus 1197-1205)
# =============================================================================
PROTOCOL_CODES_P_PUMP: Final = [
    "P01",  # Main Circulation Pump Mode (Modbus 1197)
    "P02",  # Pump Interval Time (Modbus 1198)
    "P05",  # DHW Pump Mode (Modbus 1201)
    "P06",  # Main Pump Manual Control (Modbus 1202)
    "P10",  # Circulation Pump Speed (Modbus 1205)
]

# =============================================================================
# F - FAN PARAMETERS (Read-write, Modbus 1059-1104)
# =============================================================================
PROTOCOL_CODES_F_FAN: Final = [
    "F01",  # Fan Motor Type (Modbus 1059)
    "F10",  # Fan Quantity (Modbus 1074)
    "F18",  # Min Fan Speed Cooling (Modbus 1081)
    "F19",  # Min Fan Speed Heating (Modbus 1083)
    "F22",  # Enable Manual Fan Speed (Modbus 1087)
    "F23",  # Rated DC Fan Speed (Modbus 1089)
    "F25",  # Max Fan Speed Cooling (Modbus 1103)
    "F26",  # Max Fan Speed Heating (Modbus 1104)
]

# Combined P+F for backward compatibility
PROTOCOL_CODES_PUMP_FAN: Final = PROTOCOL_CODES_P_PUMP + PROTOCOL_CODES_F_FAN

# =============================================================================
# D - DEFROST PARAMETERS (Read-write, Modbus 1105-1126)
# =============================================================================
PROTOCOL_CODES_D_DEFROST: Final = [
    "D01",  # Defrost Start Ambient Temp (Modbus 1105)
    "D02",  # Heating Time Before Defrost (Modbus 1106)
    "D03",  # Defrost Interval Time (Modbus 1107)
    "D17",  # Coil Temp Exit Defrost (Modbus 1122)
    "D19",  # Max Defrost Time (Modbus 1124)
    "D20",  # Defrost Frequency (Modbus 1125)
    "D21",  # Enable Electric Heater Defrost (Modbus 1126)
    "D26",  # Enable Cascade Defrost (Modbus 1129)
]

# Alias for backward compatibility
PROTOCOL_CODES_DEFROST: Final = PROTOCOL_CODES_D_DEFROST

# =============================================================================
# C - COMPRESSOR PARAMETERS (Read-write, Modbus 1218-1223)
# =============================================================================
PROTOCOL_CODES_C_COMPRESSOR: Final = [
    "C01",  # Manual Compressor Frequency (Modbus 1218)
    "C02",  # Min Compressor Frequency (Modbus 1219)
    "C03",  # Max Compressor Frequency (Modbus 1220)
    "C04",  # Model Selection (Modbus 1221)
    "C06",  # Frequency Control Mode (Modbus 1223)
]

# Alias for backward compatibility
PROTOCOL_CODES_COMPRESSOR: Final = PROTOCOL_CODES_C_COMPRESSOR

# =============================================================================
# G - DISINFECTION / ANTI-LEGIONELLA (Read-write, Modbus 1152-1156)
# =============================================================================
PROTOCOL_CODES_G_DISINFECTION: Final = [
    "G01",  # Disinfection Water Temp (Modbus 1152)
    "G02",  # Disinfection Duration (Modbus 1153)
    "G03",  # Disinfection Start Time (Modbus 1154)
    "G04",  # Disinfection Interval (Modbus 1155)
    "G05",  # Enable Disinfection (Modbus 1156)
]

# Alias for backward compatibility
PROTOCOL_CODES_DISINFECTION: Final = PROTOCOL_CODES_G_DISINFECTION

# =============================================================================
# Z - ZONE CONTROL (Read-write, Modbus 1069-1076)
# =============================================================================
PROTOCOL_CODES_Z_ZONE: Final = [
    "Z01",  # Enable Multi-Zone (Modbus 1069)
    "Z02",  # Zone 1 Target RT (Modbus 1070)
    "Z04",  # Zone 2 Target RT (Modbus 1072)
    "Z06",  # Zone 1 Heating Target WT (Modbus 1075)
    "Z07",  # Zone 2 Mixing Target WT (Modbus 1076)
    "Z17",  # Zone 2 AT Compensation Curve Enable
]

# Alias for backward compatibility
PROTOCOL_CODES_ZONE: Final = PROTOCOL_CODES_Z_ZONE

# =============================================================================
# E - EEV (Electronic Expansion Valve) (Read-write, Modbus 1131-1138)
# =============================================================================
PROTOCOL_CODES_E_EEV: Final = [
    "E01",  # EEV Adjust Mode (Modbus 1131)
    "E02",  # Target Superheat Heating (Modbus 1132)
    "E03",  # EEV Initial Steps Heating (Modbus 1133)
    "E07",  # EEV Min Steps (Modbus 1137)
    "E08",  # EEV Initial Steps Cooling (Modbus 1138)
]

# Alias for backward compatibility
PROTOCOL_CODES_EEV: Final = PROTOCOL_CODES_E_EEV

# =============================================================================
# O - OUTPUTS / LOAD STATUS (Read-only, Modbus 2018-2022)
# =============================================================================
PROTOCOL_CODES_O_OUTPUTS: Final = [
    "O15",  # EEV Steps (Modbus 2020)
    "O17",  # EVI EEV Steps (Modbus 2022)
    "O25",  # Load Output (Modbus 2018)
]

# Alias for backward compatibility  
PROTOCOL_CODES_OUTPUTS: Final = PROTOCOL_CODES_O_OUTPUTS

# Firmware versions - from Modbus CSV
PROTOCOL_CODES_VERSION: Final = [
    "code_version",           # Main code version (Modbus 2104)
    "MainBoard Version",      # Mainboard version (Modbus 2105)
    "DSP_version",            # DSP version (Modbus 2026)
    "PFC_version",            # PFC version (Modbus 2027)
    "DisplayVer",             # Display version (Modbus 2112)
]

# =============================================================================
# ALL PROTOCOL CODES - Full data fetch
# =============================================================================
# MUST include all params used by sensors/switches/selects/numbers
PROTOCOL_CODES_ALL: Final = (
    PROTOCOL_CODES_STATUS +           # Power, Mode, ModeState
    PROTOCOL_CODES_TEMPS +            # T01-T55 (temps, electrical, frequency)
    PROTOCOL_CODES_SETPOINTS +        # R01-R70 (target temperatures)
    PROTOCOL_CODES_ENERGY +           # Power In/Out, COP, energy consumption
    PROTOCOL_CODES_CLIMATE +          # Zone temps, indoor temp/humidity (DP4-6)
    PROTOCOL_CODES_VERSION +          # Firmware versions
    PROTOCOL_CODES_CONFIG +           # H - System config
    PROTOCOL_CODES_PROTECTION +       # A - Protection parameters
    PROTOCOL_CODES_DISINFECTION +     # G - Disinfection/Anti-legionella
    PROTOCOL_CODES_PUMP_FAN +         # P - Pump + F - Fan
    PROTOCOL_CODES_DEFROST +          # D - Defrost
    PROTOCOL_CODES_COMPRESSOR +       # C - Compressor
    PROTOCOL_CODES_ZONE +             # Z - Zone control
    PROTOCOL_CODES_EEV +              # E - EEV
    PROTOCOL_CODES_OUTPUTS            # O - Outputs/Load status
)

# Common codes for regular polling (subset for efficiency)
PROTOCOL_CODES_COMMON: Final = [
    "Power", "Mode", "ModeState",
    "T01", "T02", "T03", "T04", "T05", "T08", "T09", "T12",
    "T30", "T39",  # Compressor freq, water flow
    "R01", "R02", "R03", "R70",
    "Power In(Total)", "COP/EER(Total)",
]

# Error codes from arrays.xml and Modbus fault registers
ERROR_CODES: Final = {
    # Communication errors
    "E003": "Communication error",
    "F00": "Communication fault",
    
    # Pressure protection
    "E032": "High pressure protection",
    "E04": "Low pressure protection",
    
    # Temperature protection
    "E051": "Exhaust temperature too high",
    "E06": "Antifreeze protection",
    "E065": "Outlet water temperature too high",
    "E071": "Ambient temperature too low",
    
    # Flow errors
    "E08": "Water flow error",
    
    # Sensor faults
    "E101": "Inlet temperature sensor fault (T01)",
    "E11": "Outlet temperature sensor fault (T02)",
    "E12": "Coil temperature sensor fault (T03)",
    "E171": "High pressure sensor fault",
    "E201": "Ambient temperature sensor fault (T04)",
    
    # Motor/compressor faults  
    "E19": "Fan motor fault",
    "E21": "Compressor overcurrent",
    "E22": "Phase fault",
    
    # System faults
    "F01": "EEPROM fault",
    "F03": "Water pump fault",
}

# Modbus register mapping for direct access
MODBUS_REGISTERS: Final = {
    # Control registers (Read-Write)
    1011: "Power",
    1012: "Mode",
    1157: "R01",  # DHW Target Temp
    1158: "R02",  # Heating Target Temp
    1159: "R03",  # Cooling Target Temp
    
    # Status registers (Read-Only)
    2011: "Power State",
    2012: "ModeState",
    2045: "T01",  # Inlet Water Temp
    2046: "T02",  # Outlet Water Temp
    2047: "T08",  # DHW Tank Temp
    2048: "T04",  # Ambient Temp
    2049: "T03",  # Coil Temp
    2051: "T05",  # Suction Temp
    2052: "T07",  # Buffer Tank Temp
    2053: "T12",  # Exhaust Temp
    2054: "Power In(Total)",
    2058: "T09",  # Room Temp
    2059: "Capacity Out(Total)",
    2060: "COP/EER(Total)",
    2071: "T30",  # Compressor Frequency
    2077: "T39",  # Water Flow Rate
}

# ============================================
# MODBUS DATA TYPE CONVERSIONS
# ============================================
# Based on Modbus RTU specification from modbus_kaisai_phnix.csv
# TEMP  - Signed, 0.1°C resolution. Value / 10. 32767 = sensor fault
# DIGI1 - Unsigned, unit 1. No conversion
# DIGI2 - Unsigned, unit 10. Value / 10
# DIGI3 - Unsigned, unit 100. Value / 100
# DIGI5 - Unsigned, unit 0.1. Value / 10
# DIGI6 - Unsigned, unit 0.001. Value / 1000
# DIGI9 - Unsigned, unit 0.01. Value / 100
# ENUM  - Discrete values. No conversion
# BINARY - Bitfield. No conversion

# Data type for each protocol code (code -> (data_type, divisor))
# Note: API already returns scaled values for most codes, but we need this for Modbus direct
DATA_TYPE_MAP: Final = {
    # Temperature sensors (TEMP type - API already returns °C)
    "T01": ("TEMP", 1),
    "T02": ("TEMP", 1),
    "T03": ("TEMP", 1),
    "T04": ("TEMP", 1),
    "T05": ("TEMP", 1),
    "T06": ("TEMP", 1),
    "T07": ("TEMP", 1),
    "T08": ("TEMP", 1),
    "T09": ("TEMP", 1),
    "T10": ("TEMP", 1),
    "T11": ("TEMP", 1),
    "T12": ("TEMP", 1),
    "T14": ("TEMP", 1),
    "T33": ("TEMP", 1),
    "T38": ("TEMP", 1),
    "T49": ("TEMP", 1),
    "T50": ("TEMP", 1),
    "T51": ("TEMP", 1),
    "T55": ("TEMP", 1),
    
    # Setpoints (TEMP type)
    "R01": ("TEMP", 1),
    "R02": ("TEMP", 1),
    "R03": ("TEMP", 1),
    "R04": ("TEMP", 1),
    "R05": ("TEMP", 1),
    "R06": ("TEMP", 1),
    "R07": ("TEMP", 1),
    "R08": ("TEMP", 1),
    "R09": ("TEMP", 1),
    "R10": ("TEMP", 1),
    "R11": ("TEMP", 1),
    "R16": ("TEMP", 1),
    "R17": ("TEMP", 1),
    "R36": ("TEMP", 1),
    "R37": ("TEMP", 1),
    "R70": ("TEMP", 1),
    
    # Pressure (DIGI5 - 0.1 bar resolution)
    "T15": ("DIGI5", 10),
    
    # Current (DIGI5 - 0.1 A resolution)
    "T35": ("DIGI5", 10),
    "T36": ("DIGI5", 10),
    
    # Voltage (DIGI1 - no conversion)
    "T34": ("DIGI1", 1),
    "T37": ("DIGI1", 1),
    
    # Frequencies (DIGI1 - Hz)
    "T30": ("DIGI1", 1),
    "T31": ("DIGI1", 1),
    "T32": ("DIGI1", 1),
    
    # Fan speeds (DIGI1 - RPM)
    "T27": ("DIGI1", 1),
    "T28": ("DIGI1", 1),
    "T29": ("DIGI1", 1),
    
    # Water flow (DIGI9 - 0.01 L/min)
    "T39": ("DIGI9", 100),
    
    # Power (DIGI5 - 0.1 kW)
    "Power In(Total)": ("DIGI5", 10),
    "Capacity Out(Total)": ("DIGI5", 10),
    
    # COP/EER (DIGI9 - 0.01 resolution)
    "COP/EER(Total)": ("DIGI9", 100),
    
    # Energy (DIGI1 - kWh)
    "Comsuption Power": ("DIGI1", 1),
    
    # ODU Power (DIGI5 - 0.1 kW)
    "Power In(ODU)": ("DIGI5", 10),
    "Capacity Out(ODU)": ("DIGI5", 10),
    
    # ODU Energy consumption/generation (DIGI1 - kWh)
    "Heating Con.(ODU)": ("DIGI1", 1),
    "Heating Gen.(ODU)": ("DIGI1", 1),
    "Cooling Con.(ODU)": ("DIGI1", 1),
    "Cooling Gen.(ODU)": ("DIGI1", 1),
    "DHW Con.(ODU)": ("DIGI1", 1),
    "DHW Gen.(ODU)": ("DIGI1", 1),
    
    # Zone sensors (TEMP type)
    "Zone 1 Room Temp": ("TEMP", 1),
    "Zone 2 Room Temp": ("TEMP", 1),
    "Zone 2 Mixing Temp": ("TEMP", 1),
    
    # Zone valve (DIGI1 - percentage)
    "Zone 2 Mixing Valve": ("DIGI1", 1),
    
    # Indoor climate sensors
    "DP4": ("TEMP", 1),  # Indoor Temp
    "DP5": ("TEMP", 1),  # Indoor Humidity (uses TEMP type in Modbus but it's %)
    "DP6": ("TEMP", 1),  # Dew Point Temp
    
    # ENUM types (discrete values)
    "Power": ("ENUM", 1),
    "Mode": ("ENUM", 1),
    "ModeState": ("ENUM", 1),
    "Power State": ("ENUM", 1),
    "H01": ("ENUM", 1),
    "H05": ("ENUM", 1),
    "H07": ("ENUM", 1),
    "H18": ("ENUM", 1),
    "H20": ("ENUM", 1),
    "H21": ("ENUM", 1),
    "H22": ("ENUM", 1),
    "H25": ("ENUM", 1),
    "H27": ("ENUM", 1),
    "H28": ("ENUM", 1),
    "H30": ("ENUM", 1),
    "H31": ("ENUM", 1),
    "A11": ("ENUM", 1),
    "A29": ("ENUM", 1),
    "F01": ("ENUM", 1),
    "F10": ("ENUM", 1),
    "F22": ("ENUM", 1),
    "G05": ("ENUM", 1),
    "Z01": ("ENUM", 1),
}

# Writable parameters with their ranges and units
# Organized by category: R=Temps, Z=Zones, G=Disinfection, C=Compressor, P=Pump, F=Fan, D=Defrost, A=Protection, E=EEV, H=System
WRITABLE_PARAMS: Final = {
    # === TEMPERATURES (R) - Main setpoints ===
    "R01": {"name": "DHW Target Temp", "min": 20, "max": 65, "step": 0.5, "unit": "°C", "category": "temperatures"},
    "R02": {"name": "Heating Target Temp", "min": 20, "max": 65, "step": 0.5, "unit": "°C", "category": "temperatures"},
    "R03": {"name": "Cooling Target Temp", "min": 7, "max": 25, "step": 0.5, "unit": "°C", "category": "temperatures"},
    "R70": {"name": "Room Target Temp", "min": 5, "max": 27, "step": 0.5, "unit": "°C", "category": "temperatures"},
    # Temperature differences (hysteresis)
    "R04": {"name": "Heating On Diff", "min": 0, "max": 10, "step": 0.5, "unit": "°C", "category": "temperatures"},
    "R05": {"name": "Heating Off Diff", "min": 0, "max": 10, "step": 0.5, "unit": "°C", "category": "temperatures"},
    "R06": {"name": "Cooling On Diff", "min": 0, "max": 10, "step": 0.5, "unit": "°C", "category": "temperatures"},
    "R07": {"name": "Cooling Off Diff", "min": 0, "max": 10, "step": 0.5, "unit": "°C", "category": "temperatures"},
    "R16": {"name": "DHW On Diff", "min": 0, "max": 10, "step": 0.5, "unit": "°C", "category": "temperatures"},
    "R17": {"name": "DHW Off Diff", "min": 0, "max": 10, "step": 0.5, "unit": "°C", "category": "temperatures"},
    # Temperature limits
    "R08": {"name": "Min Cooling Target", "min": 5, "max": 25, "step": 1, "unit": "°C", "category": "temperatures"},
    "R09": {"name": "Max Cooling Target", "min": 10, "max": 30, "step": 1, "unit": "°C", "category": "temperatures"},
    "R10": {"name": "Min Heating Target", "min": 15, "max": 45, "step": 1, "unit": "°C", "category": "temperatures"},
    "R11": {"name": "Max Heating Target", "min": 35, "max": 75, "step": 1, "unit": "°C", "category": "temperatures"},
    "R36": {"name": "Min DHW Target", "min": 15, "max": 50, "step": 1, "unit": "°C", "category": "temperatures"},
    "R37": {"name": "Max DHW Target", "min": 40, "max": 70, "step": 1, "unit": "°C", "category": "temperatures"},
    
    # === ZONES (Z) ===
    "Z02": {"name": "Zone 1 Target RT", "min": 10, "max": 35, "step": 0.5, "unit": "°C", "category": "zones"},
    "Z03": {"name": "Zone 1 Diff to Start", "min": 0, "max": 10, "step": 0.5, "unit": "°C", "category": "zones"},
    "Z04": {"name": "Zone 2 Target RT", "min": 10, "max": 35, "step": 0.5, "unit": "°C", "category": "zones"},
    "Z05": {"name": "Zone 2 Diff to Start", "min": 0, "max": 10, "step": 0.5, "unit": "°C", "category": "zones"},
    "Z06": {"name": "Zone 1 Heating Target WT", "min": 20, "max": 65, "step": 0.5, "unit": "°C", "category": "zones"},
    "Z07": {"name": "Zone 2 Mixing Target WT", "min": 20, "max": 65, "step": 0.5, "unit": "°C", "category": "zones"},
    "Z08": {"name": "Mixing Valve Manual %", "min": 0, "max": 100, "step": 1, "unit": "%", "category": "zones"},
    "Z09": {"name": "Mixing Valve Open Time", "min": 0, "max": 2000, "step": 10, "unit": "s", "category": "zones"},
    "Z10": {"name": "Mixing Valve Close Time", "min": 0, "max": 2000, "step": 10, "unit": "s", "category": "zones"},
    "Z11": {"name": "Mixing Valve P", "min": 0, "max": 10, "step": 0.1, "unit": "", "category": "zones"},
    "Z12": {"name": "Mixing Valve I", "min": 0, "max": 10, "step": 0.1, "unit": "", "category": "zones"},
    "Z13": {"name": "Mixing Valve PID Period", "min": 1, "max": 20, "step": 1, "unit": "min", "category": "zones"},
    
    # === DISINFECTION (G) - Anti-Legionella ===
    "G01": {"name": "Disinfection Temp", "min": 60, "max": 75, "step": 1, "unit": "°C", "category": "disinfection"},
    "G02": {"name": "Disinfection Duration", "min": 5, "max": 60, "step": 5, "unit": "min", "category": "disinfection"},
    "G03": {"name": "Disinfection Start Time", "min": 0, "max": 23, "step": 1, "unit": "h", "category": "disinfection"},
    "G04": {"name": "Disinfection Interval", "min": 1, "max": 30, "step": 1, "unit": "days", "category": "disinfection"},

    # === COMPRESSOR (C) ===
    "C01": {"name": "Manual Comp Freq", "min": 0, "max": 120, "step": 1, "unit": "Hz", "category": "compressor"},
    "C02": {"name": "Min Comp Freq", "min": 20, "max": 60, "step": 1, "unit": "Hz", "category": "compressor"},
    "C03": {"name": "Max Comp Freq", "min": 50, "max": 120, "step": 1, "unit": "Hz", "category": "compressor"},
    
    # === PUMP (P) ===
    "P02": {"name": "Pump Interval Time", "min": 0, "max": 60, "step": 1, "unit": "min", "category": "pump"},
    "P10": {"name": "Circulation Pump Speed", "min": 0, "max": 100, "step": 5, "unit": "%", "category": "pump"},
    
    # === FAN (F) ===
    "F02": {"name": "CT Max Fan Cooling", "min": -15, "max": 60, "step": 1, "unit": "°C", "category": "fan"},
    "F03": {"name": "CT Min Fan Cooling", "min": -15, "max": 60, "step": 1, "unit": "°C", "category": "fan"},
    "F05": {"name": "CT Max Fan Heating", "min": -15, "max": 60, "step": 1, "unit": "°C", "category": "fan"},
    "F06": {"name": "CT Min Fan Heating", "min": -15, "max": 60, "step": 1, "unit": "°C", "category": "fan"},
    "F18": {"name": "Min Fan Speed Cooling", "min": 10, "max": 1300, "step": 10, "unit": "rpm", "category": "fan"},
    "F19": {"name": "Min Fan Speed Heating", "min": 10, "max": 1300, "step": 10, "unit": "rpm", "category": "fan"},
    "F23": {"name": "Rated DC Fan Speed", "min": 10, "max": 1300, "step": 10, "unit": "rpm", "category": "fan"},
    "F25": {"name": "Max Fan Speed Cooling", "min": 10, "max": 1300, "step": 10, "unit": "rpm", "category": "fan"},
    "F26": {"name": "Max Fan Speed Heating", "min": 10, "max": 1300, "step": 10, "unit": "rpm", "category": "fan"},
    "F28": {"name": "CT Two to One Fan Cooling", "min": -30, "max": 60, "step": 1, "unit": "°C", "category": "fan"},
    "F29": {"name": "CT Stop Single Fan Cooling", "min": -30, "max": 60, "step": 1, "unit": "°C", "category": "fan"},
    
    # === DEFROST (D) ===
    "D01": {"name": "Defrost Start AT", "min": -37, "max": 45, "step": 1, "unit": "°C", "category": "defrost"},
    "D02": {"name": "Heating Before Defrost", "min": 0, "max": 120, "step": 5, "unit": "min", "category": "defrost"},
    "D03": {"name": "Defrost Interval", "min": 10, "max": 90, "step": 5, "unit": "min", "category": "defrost"},
    "D17": {"name": "CT Exit Defrost", "min": 0, "max": 30, "step": 1, "unit": "°C", "category": "defrost"},
    "D19": {"name": "Max Defrost Time", "min": 1, "max": 20, "step": 1, "unit": "min", "category": "defrost"},
    "D20": {"name": "Defrost Frequency", "min": 20, "max": 120, "step": 5, "unit": "Hz", "category": "defrost"},
    
    # === PROTECTION (A) ===
    "A03": {"name": "Shutdown Ambient Temp", "min": -40, "max": 10, "step": 1, "unit": "°C", "category": "protection"},
    "A04": {"name": "Antifreeze Temp", "min": -20, "max": 10, "step": 0.5, "unit": "°C", "category": "protection"},
    "A05": {"name": "Antifreeze Temp Diff", "min": 1, "max": 50, "step": 0.5, "unit": "°C", "category": "protection"},
    "A06": {"name": "Max Exhaust Temp", "min": 60, "max": 130, "step": 1, "unit": "°C", "category": "protection"},
    "A22": {"name": "Min Antifreeze Temp", "min": -20, "max": 10, "step": 0.5, "unit": "°C", "category": "protection"},
    "A23": {"name": "Min Outlet Water Protect", "min": -30, "max": 20, "step": 1, "unit": "°C", "category": "protection"},
    "A24": {"name": "Excess Temp Diff In/Out", "min": 0, "max": 30, "step": 1, "unit": "°C", "category": "protection"},
    "A25": {"name": "Min Evap Temp Cooling", "min": -50, "max": 30, "step": 1, "unit": "°C", "category": "protection"},
    "A27": {"name": "Temp Diff Limit Freq", "min": -20, "max": 95, "step": 1, "unit": "°C", "category": "protection"},
    "A28": {"name": "Temp Diff Outlet/DHW", "min": -20, "max": 95, "step": 1, "unit": "°C", "category": "protection"},
    "A30": {"name": "Min AT for Cooling", "min": -30, "max": 60, "step": 1, "unit": "°C", "category": "protection"},
    "A31": {"name": "Electric Heater On AT", "min": -30, "max": 60, "step": 1, "unit": "°C", "category": "protection"},
    "A32": {"name": "E-Heater Delays Comp", "min": 10, "max": 999, "step": 10, "unit": "min", "category": "protection"},
    "A33": {"name": "E-Heater Opening Diff", "min": 0, "max": 20, "step": 1, "unit": "°C", "category": "protection"},
    "A34": {"name": "Crank Preheating Time", "min": 0, "max": 360, "step": 10, "unit": "min", "category": "protection"},
    "A35": {"name": "E-Heater OFF Diff", "min": 0, "max": 30, "step": 1, "unit": "°C", "category": "protection"},
    
    # === EEV (E) - Electronic Expansion Valve ===
    "E02": {"name": "Target Superheat Heating", "min": 0, "max": 20, "step": 0.5, "unit": "°C", "category": "eev"},
    "E03": {"name": "EEV Initial Steps Heating", "min": 0, "max": 500, "step": 10, "unit": "", "category": "eev"},
    "E07": {"name": "EEV Min Steps", "min": 0, "max": 100, "step": 5, "unit": "", "category": "eev"},
    "E08": {"name": "EEV Initial Steps Cooling", "min": 0, "max": 500, "step": 10, "unit": "", "category": "eev"},
    
    # === SYSTEM (H) ===
    "H10": {"name": "Unit Address", "min": 1, "max": 32, "step": 1, "unit": "", "category": "system"},
    "H18": {"name": "Electric Heater Stage", "min": 1, "max": 3, "step": 1, "unit": "", "category": "system"},
    "H29": {"name": "Operation Code", "min": 0, "max": 20, "step": 1, "unit": "", "category": "system"},
    "H32": {"name": "Force Switch Mode Time", "min": 1, "max": 300, "step": 5, "unit": "min", "category": "system"},
}

# Switch parameters (binary on/off)
# Categories: H=System, G=Disinfection, A=Protection, F=Fan, D=Defrost, P=Pump, Z=Zone
SWITCH_PARAMS: Final = {
    # Main control
    "Power": {"name": "Power", "icon": "mdi:power", "category": "system"},
    # System (H)
    "H01": {"name": "Power-off Memory", "icon": "mdi:memory", "category": "system"},
    "H05": {"name": "Cooling Function", "icon": "mdi:snowflake", "category": "system"},
    "H22": {"name": "Silent Mode", "icon": "mdi:volume-off", "category": "system"},
    "H27": {"name": "EVI Function", "icon": "mdi:molecule", "category": "system"},
    "H33": {"name": "Fan+Comp Driver Integrated", "icon": "mdi:chip", "category": "system"},
    "H36": {"name": "Weather Compensation", "icon": "mdi:weather-cloudy", "category": "system"},
    "H45": {"name": "Show COP and Heating Output", "icon": "mdi:gauge", "category": "system"},
    # Disinfection (G)
    "G05": {"name": "Disinfection", "icon": "mdi:bacteria", "category": "disinfection"},
    # Protection (A)
    "A11": {"name": "Low Pressure Sensor", "icon": "mdi:gauge-low", "category": "protection"},
    "A29": {"name": "High Pressure Sensor", "icon": "mdi:gauge-full", "category": "protection"},
    # Fan (F)
    "F22": {"name": "Manual Fan Speed", "icon": "mdi:fan", "category": "fan"},
    # Defrost (D)
    "D21": {"name": "Electric Heater Defrost", "icon": "mdi:heating-coil", "category": "defrost"},
    "D26": {"name": "Defrost Communication Cascade", "icon": "mdi:link-variant", "category": "defrost"},
    # Zone (Z)
    "Z17": {"name": "AT Compensation Curve Zone 2", "icon": "mdi:chart-line", "category": "zones"},
}

# Select parameters (multi-option)
# Categories: H=System, Z=Zone, F=Fan, C=Compressor, P=Pump, A=Protection, E=EEV
SELECT_PARAMS: Final = {
    # Main control
    "Mode": {
        "name": "Operating Mode",
        "icon": "mdi:hvac",
        "category": "system",
        "options": {
            "0": "Ciepła woda",
            "1": "Ogrzewanie",
            "2": "Chłodzenie",
            "3": "CW + Ogrzewanie",
            "4": "CW + Chłodzenie",
        },
    },
    # System (H)
    "H07": {
        "name": "Control Mode",
        "icon": "mdi:remote",
        "category": "system",
        "options": {
            "0": "Display Control",
            "1": "Remote Control",
        },
    },
    "H18": {
        "name": "Electric Heater Stage",
        "icon": "mdi:heating-coil",
        "category": "system",
        "options": {
            "1": "Stage 1",
            "2": "Stage 2",
            "3": "Stage 3",
        },
    },
    "H20": {
        "name": "3-way Valve Polarity",
        "icon": "mdi:valve",
        "category": "system",
        "options": {
            "0": "CWU - ZAŁ",
            "1": "CWU - WYŁ",
        },
    },
    "H21": {
        "name": "Temperature Unit",
        "icon": "mdi:thermometer",
        "category": "system",
        "options": {
            "0": "°C",
            "1": "°F",
        },
    },
    "H25": {
        "name": "Temp Control Selection",
        "icon": "mdi:target",
        "category": "system",
        "options": {
            "0": "Outlet Water Temp",
            "1": "Room Temp",
            "2": "Buffer Tank Temp",
            "3": "Inlet Water Temp",
        },
    },
    "H28": {
        "name": "DHW Function",
        "icon": "mdi:water-boiler",
        "category": "system",
        "options": {
            "0": "Disabled",
            "1": "Enabled",
            "2": "Only DHW",
        },
    },
    "H30": {
        "name": "Indoor Unit Type",
        "icon": "mdi:hvac",
        "category": "system",
        "options": {
            "0": "None",
            "1": "Type 1",
            "2": "Type 2",
            "3": "Type 3",
        },
    },
    "H31": {
        "name": "Circulation Pump Type",
        "icon": "mdi:pump",
        "category": "system",
        "options": {
            "0": "No Flow Detection",
            "1": "Grundfos 25-75",
            "2": "Grundfos 25-105",
            "3": "Grundfos 25-125",
            "4": "APM25 9-130",
            "5": "APM25 12-130",
        },
    },
    "H37": {
        "name": "DHW Temp Sourcing",
        "icon": "mdi:thermometer",
        "category": "system",
        "options": {
            "0": "DHW Tank Sensor",
            "1": "External Modbus",
        },
    },
    "H38": {
        "name": "Language",
        "icon": "mdi:translate",
        "category": "system",
        "options": {
            "0": "English",
            "1": "Chinese",
            "2": "Polish",
            "3": "German",
            "4": "French",
            "5": "Italian",
            "6": "Spanish",
            "7": "Portuguese",
            "8": "Russian",
            "9": "Czech",
            "10": "Hungarian",
            "11": "Romanian",
            "12": "Turkish",
            "13": "Greek",
        },
    },
    # Zone (Z)
    "Z01": {
        "name": "Multi-Zone Control",
        "icon": "mdi:home-group",
        "category": "zones",
        "options": {
            "0": "None",
            "1": "Zone 1-S",
            "2": "Zone 2-S",
            "3": "Zone 1&2-S",
            "4": "Zone 1-T",
            "5": "Zone 2-T",
            "6": "Zone 1&2-T",
            "7": "Zone 1-P",
            "8": "Zone 2-P",
            "9": "Zone 1&2-P",
        },
    },
    # Fan (F)
    "F01": {
        "name": "Fan Motor Type",
        "icon": "mdi:fan",
        "category": "fan",
        "options": {
            "1": "Double",
            "3": "DC",
            "4": "DC External Drive",
        },
    },
    "F10": {
        "name": "Fan Quantity",
        "icon": "mdi:fan",
        "category": "fan",
        "options": {
            "0": "One Fan",
            "1": "Two Fans",
        },
    },
    # Compressor (C)
    "C04": {
        "name": "Model Selection",
        "icon": "mdi:cog",
        "category": "compressor",
        "options": {
            "0": "Model 0",
            "1": "Model 1",
            "2": "Model 2",
            "3": "Model 3",
        },
    },
    "C06": {
        "name": "Frequency Control Mode",
        "icon": "mdi:sine-wave",
        "category": "compressor",
        "options": {
            "0": "Auto",
            "1": "Manual",
        },
    },
    # Pump (P)
    "P01": {
        "name": "Main Pump Mode",
        "icon": "mdi:pump",
        "category": "pump",
        "options": {
            "0": "Continuous",
            "1": "Interval",
            "2": "On Demand",
        },
    },
    "P05": {
        "name": "DHW Pump Mode",
        "icon": "mdi:pump",
        "category": "pump",
        "options": {
            "0": "Off",
            "1": "On",
            "2": "Auto",
        },
    },
    "P06": {
        "name": "Main Pump Manual Control",
        "icon": "mdi:pump",
        "category": "pump",
        "options": {
            "0": "Auto",
            "1": "Manual On",
            "2": "Manual Off",
        },
    },
    # Protection (A)
    "A21": {
        "name": "Sensor Type",
        "icon": "mdi:thermometer",
        "category": "protection",
        "options": {
            "0": "5K",
            "1": "2K",
        },
    },
    "A26": {
        "name": "Refrigerant Type",
        "icon": "mdi:molecule",
        "category": "protection",
        "options": {
            "0": "R32",
            "1": "R290",
            "2": "R32-1",
            "3": "R290-1",
            "4": "R32-2",
            "5": "R290-2",
        },
    },
    # EEV (E)
    "E01": {
        "name": "EEV Adjust Mode",
        "icon": "mdi:tune-variant",
        "category": "eev",
        "options": {
            "0": "Auto",
            "1": "Manual",
        },
    },
}

# ============================================
# COMPLETE PARAMETER SETS FROM MODBUS CSV
# ============================================
# Use the comprehensive parameters generated from modbus_kaisai_phnix.csv
# Total: 303 writable, 167 sensors, 46 switches, 34 selects
# These include all Modbus addresses, data types, ranges, and categories

# All writable number parameters (sliders, inputs)
ALL_WRITABLE_PARAMS: Final = MODBUS_WRITABLE_PARAMS

# All sensor parameters (read-only values)
ALL_SENSOR_PARAMS: Final = MODBUS_SENSOR_PARAMS

# All switch parameters (binary on/off)
ALL_SWITCH_PARAMS: Final = MODBUS_SWITCH_PARAMS

# All select parameters (multi-option dropdowns)
ALL_SELECT_PARAMS: Final = MODBUS_SELECT_PARAMS

# Helper function to get entity name with parameter code prefix
def get_entity_name_with_code(code: str, name: str, language: str = "en") -> str:
    """Generate entity name with parameter code prefix like '[R01] DHW Target Temp'."""
    return f"[{code}] {name}"

# Combined list of all protocol codes to request from API
ALL_PROTOCOL_CODES: Final = (
    list(ALL_WRITABLE_PARAMS.keys()) +
    list(ALL_SENSOR_PARAMS.keys()) +
    list(ALL_SWITCH_PARAMS.keys()) +
    list(ALL_SELECT_PARAMS.keys())
)
