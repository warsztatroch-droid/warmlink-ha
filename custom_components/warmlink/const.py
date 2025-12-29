"""Constants for the Warmlink integration."""
from typing import Final

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
PROTOCOL_CODES_STATUS: Final = [
    "Power",        # 0=off, 1=on (Modbus 1011)
    "Mode",         # 0=HotWater, 1=Heating, 2=Cooling, 3=HW+Heating, 4=HW+Cooling (Modbus 1012)
    "ModeState",    # Read-only: 0=Cooling, 1=Heating, 2=Defrost, 3=Disinfection, 4=HotWater (Modbus 2012)
    "Power State",  # Read-only power state (Modbus 2011)
]

# Temperature sensors - from Modbus CSV registers 2045-2068
PROTOCOL_CODES_TEMPS: Final = [
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
    "T12",  # Exhaust Temp (Modbus 2053)
    "T14",  # Distributor Tube Temp (Modbus 2050)
    "T15",  # Low Pressure (Modbus 2069)
    "T30",  # Compressor Frequency (Modbus 2071)
    "T31",  # Compressor Working Frequency (Modbus 2072)
    "T34",  # AC Input Voltage (Modbus 2062)
    "T35",  # AC Input Current (Modbus 2057)
    "T36",  # Compressor Phase Current (Modbus 2042)
    "T37",  # DC Bus Voltage (Modbus 2043)
    "T38",  # IPM Temp (Modbus 2044)
    "T39",  # Water Flow Rate (Modbus 2077)
    "T49",  # Evaporation Temperature (Modbus 2065)
    "T50",  # Exhaust Superheat (Modbus 2066)
    "T51",  # Superheat (Modbus 2067)
]

# Setpoints - from Modbus CSV registers 1157-1177
PROTOCOL_CODES_SETPOINTS: Final = [
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

# Energy and Performance - from Modbus CSV
PROTOCOL_CODES_ENERGY: Final = [
    "Power In(Total)",      # Total Power Input kW (Modbus 2054)
    "Capacity Out(Total)",  # Total Capacity Output kW (Modbus 2059)
    "COP/EER(Total)",       # COP/EER (Modbus 2060)
    "Comsuption Power",     # Consumption kWh (Modbus 2078+2079)
]

# Configuration parameters - from Modbus CSV
PROTOCOL_CODES_CONFIG: Final = [
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
    "H36",  # Enable Weather Compensation (Modbus 1236)
]

# Protection parameters - from Modbus CSV
PROTOCOL_CODES_PROTECTION: Final = [
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
]

# Pump and Fan - from Modbus CSV
PROTOCOL_CODES_PUMP_FAN: Final = [
    "P01",  # Main Circulation Pump Mode (Modbus 1197)
    "P02",  # Pump Interval Time (Modbus 1198)
    "P05",  # DHW Pump Mode (Modbus 1201)
    "P06",  # Main Pump Manual Control (Modbus 1202)
    "P10",  # Circulation Pump Speed (Modbus 1205)
    "F01",  # Fan Motor Type (Modbus 1059)
    "F10",  # Fan Quantity (Modbus 1074)
    "F18",  # Min Fan Speed Cooling (Modbus 1081)
    "F19",  # Min Fan Speed Heating (Modbus 1083)
    "F22",  # Enable Manual Fan Speed (Modbus 1087)
    "F23",  # Rated DC Fan Speed (Modbus 1089)
    "F25",  # Max Fan Speed Cooling (Modbus 1103)
    "F26",  # Max Fan Speed Heating (Modbus 1104)
    "T27",  # Fan Motor 1 Speed (Modbus 2074)
    "T28",  # Fan Motor 2 Speed (Modbus 2075)
]

# Defrosting parameters - from Modbus CSV
PROTOCOL_CODES_DEFROST: Final = [
    "D01",  # Defrost Start Ambient Temp (Modbus 1105)
    "D02",  # Heating Time Before Defrost (Modbus 1106)
    "D03",  # Defrost Interval Time (Modbus 1107)
    "D17",  # Coil Temp Exit Defrost (Modbus 1122)
    "D19",  # Max Defrost Time (Modbus 1124)
    "D20",  # Defrost Frequency (Modbus 1125)
    "D21",  # Enable Electric Heater Defrost (Modbus 1126)
]

# Compressor parameters - from Modbus CSV
PROTOCOL_CODES_COMPRESSOR: Final = [
    "C01",  # Manual Compressor Frequency (Modbus 1218)
    "C02",  # Min Compressor Frequency (Modbus 1219)
    "C03",  # Max Compressor Frequency (Modbus 1220)
    "C04",  # Model Selection (Modbus 1221)
    "C06",  # Frequency Control Mode (Modbus 1223)
]

# Disinfection (anti-legionella) - from Modbus CSV
PROTOCOL_CODES_DISINFECTION: Final = [
    "G01",  # Disinfection Water Temp (Modbus 1152)
    "G02",  # Disinfection Duration (Modbus 1153)
    "G03",  # Disinfection Start Time (Modbus 1154)
    "G04",  # Disinfection Interval (Modbus 1155)
    "G05",  # Enable Disinfection (Modbus 1156)
]

# Zone control - from Modbus CSV
PROTOCOL_CODES_ZONE: Final = [
    "Z01",  # Enable Multi-Zone (Modbus 1069)
    "Z02",  # Zone 1 Target RT (Modbus 1070)
    "Z04",  # Zone 2 Target RT (Modbus 1072)
    "Z06",  # Zone 1 Heating Target WT (Modbus 1075)
    "Z07",  # Zone 2 Mixing Target WT (Modbus 1076)
]

# EEV (Electronic Expansion Valve) - from Modbus CSV
PROTOCOL_CODES_EEV: Final = [
    "E01",  # EEV Adjust Mode (Modbus 1131)
    "E02",  # Target Superheat Heating (Modbus 1132)
    "E03",  # EEV Initial Steps Heating (Modbus 1133)
    "E07",  # EEV Min Steps (Modbus 1137)
    "E08",  # EEV Initial Steps Cooling (Modbus 1138)
    "O15",  # EEV Steps read-only (Modbus 2020)
    "O17",  # EVI EEV Steps read-only (Modbus 2022)
]

# Outputs/Load status - from Modbus CSV
PROTOCOL_CODES_OUTPUTS: Final = [
    "O01~023",  # Load Output status (Modbus 2019)
    "O25",      # Load Output (Modbus 2018)
]

# Firmware versions - from Modbus CSV
PROTOCOL_CODES_VERSION: Final = [
    "code_version",           # Main code version (Modbus 2104)
    "MainBoard Version",      # Mainboard version (Modbus 2105)
    "DSP_version",            # DSP version (Modbus 2026)
    "PFC_version",            # PFC version (Modbus 2027)
    "DisplayVer",             # Display version (Modbus 2112)
]

# All protocol codes for full data fetch
PROTOCOL_CODES_ALL: Final = (
    PROTOCOL_CODES_STATUS + 
    PROTOCOL_CODES_TEMPS + 
    PROTOCOL_CODES_SETPOINTS +
    PROTOCOL_CODES_ENERGY +
    PROTOCOL_CODES_VERSION
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
