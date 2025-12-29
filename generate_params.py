#!/usr/bin/env python3
"""
Generate parameters dictionary from Modbus CSV file.
Exports WRITABLE_PARAMS, SENSOR_PARAMS with proper data types and ranges.
"""

import csv
import re
import sys

# Data type to unit mapping
DATA_TYPE_UNITS = {
    "TEMP": "°C",
    "DIGI1": "",
    "DIGI2": "",
    "DIGI3": "",
    "DIGI5": "",  # /10
    "DIGI6": "",  # /1000
    "DIGI9": "",  # /100
    "ENUM": "",
    "BINARY": "",
}

# Data type to divisor
DATA_TYPE_DIVISOR = {
    "TEMP": 10,
    "DIGI1": 1,
    "DIGI2": 10,
    "DIGI3": 100,
    "DIGI5": 10,
    "DIGI6": 1000,
    "DIGI9": 100,
    "ENUM": 1,
    "BINARY": 1,
}

def parse_range(range_str: str, data_type: str) -> tuple:
    """Parse range string like '0~100' or '-30~60' into (min, max)."""
    if not range_str or range_str == "--" or range_str == "-":
        return None, None
    
    # Handle reference ranges like $1053$~10
    if "$" in range_str:
        return None, None
    
    # Clean up the string
    range_str = range_str.replace("℃", "").replace("°C", "").replace("r", "")
    range_str = range_str.replace("min", "").replace("s", "").replace("h", "")
    range_str = range_str.replace("%", "").replace("bar", "").replace("Bar", "")
    range_str = range_str.replace("kW", "").replace("W", "").replace("Hz", "")
    range_str = range_str.replace("N", "").replace("days", "")
    range_str = range_str.strip()
    
    # Handle ranges like "0~1" or "-30~60" or "0.0~20.0"
    match = re.match(r'(-?[\d.]+)[~\-](-?[\d.]+)', range_str)
    if match:
        try:
            min_val = float(match.group(1))
            max_val = float(match.group(2))
            return min_val, max_val
        except ValueError:
            return None, None
    
    return None, None

def get_category(code: str) -> str:
    """Determine category from parameter code."""
    if not code or code == "--":
        return "other"
    
    first_char = code[0].upper()
    categories = {
        "T": "temperatures",
        "R": "setpoints",
        "H": "system",
        "A": "protection",
        "F": "fan",
        "D": "defrost",
        "G": "disinfection",
        "C": "compressor",
        "P": "pump",
        "E": "eev",
        "Z": "zones",
        "S": "status",
        "O": "outputs",
    }
    return categories.get(first_char, "other")

def get_unit(name: str, data_type: str, range_str: str) -> str:
    """Determine unit from name and data type."""
    name_lower = name.lower()
    
    if "temp" in name_lower or "°c" in range_str.lower() or "℃" in range_str:
        return "°C"
    if "pressure" in name_lower or "bar" in range_str.lower():
        return "bar"
    if "current" in name_lower:
        return "A"
    if "voltage" in name_lower:
        return "V"
    if "frequency" in name_lower or "freq" in name_lower:
        return "Hz"
    if "speed" in name_lower and "fan" in name_lower:
        return "rpm"
    if "time" in name_lower or "duration" in name_lower or "min" in range_str:
        return "min"
    if "power" in name_lower and "kw" in name_lower.lower():
        return "kW"
    if "flow" in name_lower:
        return "L/min"
    if "%" in range_str or "ratio" in name_lower:
        return "%"
    if "days" in range_str:
        return "days"
    if "hour" in name_lower:
        return "h"
    if "steps" in name_lower:
        return "steps"
    
    return ""

def parse_csv(filename: str):
    """Parse Modbus CSV and generate parameter dictionaries."""
    writable_params = {}
    sensor_params = {}
    switch_params = {}
    select_params = {}
    
    with open(filename, 'r', encoding='utf-8') as f:
        # Skip header lines starting with #
        lines = [line for line in f if not line.startswith('#')]
    
    # Parse CSV
    reader = csv.reader(lines)
    header = next(reader, None)  # Skip header row
    
    for row in reader:
        if len(row) < 8:
            continue
        
        address = row[0].strip()
        if not address.isdigit():
            continue
        
        address = int(address)
        name = row[1].strip()
        code = row[2].strip()
        mode = row[4].strip()
        description = row[5].strip()
        data_type = row[6].strip()
        range_str = row[7].strip() if len(row) > 7 else ""
        
        # Skip test/internal parameters
        if code.startswith("test") or code == "--" or name.startswith("test"):
            continue
        if code.isdigit():  # Skip unnamed parameters like "1014"
            continue
        
        min_val, max_val = parse_range(range_str, data_type)
        category = get_category(code)
        unit = get_unit(name, data_type, range_str)
        
        param_info = {
            "address": address,
            "name": name,
            "code": code,
            "data_type": data_type,
            "category": category,
            "unit": unit,
        }
        
        if min_val is not None:
            param_info["min"] = min_val
        if max_val is not None:
            param_info["max"] = max_val
        
        # Determine step based on data type
        if data_type == "TEMP":
            param_info["step"] = 0.5
        elif data_type in ("DIGI5", "DIGI9"):
            param_info["step"] = 0.1
        elif min_val is not None and max_val is not None:
            range_size = max_val - min_val
            if range_size <= 10:
                param_info["step"] = 1
            elif range_size <= 100:
                param_info["step"] = 5
            else:
                param_info["step"] = 10
        else:
            param_info["step"] = 1
        
        # Add description if present
        if description and description != "--":
            param_info["description"] = description
        
        # Classify by mode and type
        if mode == "Read-write":
            if data_type == "ENUM":
                # Check if binary (0-1) switch or multi-option select
                if "0-【NO】" in description or "0-NO" in description or range_str == "0~1":
                    switch_params[code] = param_info
                else:
                    select_params[code] = param_info
            elif data_type == "BINARY":
                # Binary is special - manual control
                switch_params[code] = param_info
            else:
                writable_params[code] = param_info
        else:  # Read-only
            sensor_params[code] = param_info
    
    return writable_params, sensor_params, switch_params, select_params

def print_dict(name: str, params: dict, indent: str = "    "):
    """Print dictionary in Python format."""
    print(f"{name} = {{")
    for code, info in sorted(params.items(), key=lambda x: (x[1].get("category", ""), x[0])):
        # Format with code in name
        category = info.get("category", "other")
        data_type = info.get("data_type", "DIGI1")
        unit = info.get("unit", "")
        min_val = info.get("min")
        max_val = info.get("max")
        step = info.get("step", 1)
        address = info.get("address", 0)
        name_str = info.get("name", code)
        
        parts = [
            f'"name": "{name_str}"',
            f'"address": {address}',
            f'"data_type": "{data_type}"',
            f'"category": "{category}"',
        ]
        
        if min_val is not None:
            parts.append(f'"min": {min_val}')
        if max_val is not None:
            parts.append(f'"max": {max_val}')
        if step:
            parts.append(f'"step": {step}')
        if unit:
            parts.append(f'"unit": "{unit}"')
        
        print(f'{indent}"{code}": {{{", ".join(parts)}}},')
    
    print("}")

if __name__ == "__main__":
    csv_file = "modbus_kaisai_phnix.csv"
    
    writable, sensors, switches, selects = parse_csv(csv_file)
    
    print(f"# Generated from {csv_file}")
    print(f"# Total: {len(writable)} writable, {len(sensors)} sensors, {len(switches)} switches, {len(selects)} selects")
    print()
    
    print("# WRITABLE PARAMETERS (Number entities)")
    print_dict("WRITABLE_PARAMS", writable)
    print()
    
    print("# SENSOR PARAMETERS (Read-only)")
    print_dict("SENSOR_PARAMS", sensors)
    print()
    
    print("# SWITCH PARAMETERS (Binary on/off)")
    print_dict("SWITCH_PARAMS", switches)
    print()
    
    print("# SELECT PARAMETERS (Multi-option)")
    print_dict("SELECT_PARAMS", selects)
