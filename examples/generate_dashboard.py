#!/usr/bin/env python3
"""
Skrypt do automatycznego generowania dashboard.yaml z poprawnym DEVICE_CODE.

Użycie:
    python3 generate_dashboard.py DEVICE_CODE

Przykład:
    python3 generate_dashboard.py abc123def

Gdzie znaleźć DEVICE_CODE:
    1. Home Assistant → Settings → Devices & Services → Warmlink
    2. Kliknij na urządzenie
    3. Zobacz entity_id np. sensor.warmlink_abc123def_t01
    4. DEVICE_CODE = abc123def (środkowa część)
"""

import sys
import os

TEMPLATE = '''# Warmlink Heat Pump Dashboard
# Wygenerowano automatycznie dla urządzenia: {device_code}

title: Pompa Ciepła Warmlink
views:
  - title: Przegląd
    path: overview
    icon: mdi:heat-pump
    cards:
      # Status
      - type: entities
        title: Status
        entities:
          - entity: binary_sensor.warmlink_{device_code}_online
            name: Status połączenia
          - entity: binary_sensor.warmlink_{device_code}_power
            name: Zasilanie
          - entity: sensor.warmlink_{device_code}_modestate
            name: Tryb pracy
          - entity: binary_sensor.warmlink_{device_code}_fault
            name: Awaria

      # Climate
      - type: thermostat
        entity: climate.warmlink_{device_code}
        name: Pompa Ciepła

      # Temperatury
      - type: horizontal-stack
        cards:
          - type: gauge
            entity: sensor.warmlink_{device_code}_t01
            name: Wlot
            min: 0
            max: 70
            severity:
              green: 25
              yellow: 45
              red: 55
          - type: gauge
            entity: sensor.warmlink_{device_code}_t02
            name: Wylot
            min: 0
            max: 70
            severity:
              green: 25
              yellow: 45
              red: 55
          - type: gauge
            entity: sensor.warmlink_{device_code}_t04
            name: Zewn.
            min: -30
            max: 40
            severity:
              green: 0
              yellow: -10
              red: -20

      # Przełączniki
      - type: entities
        title: Przełączniki
        show_header_toggle: false
        entities:
          - entity: switch.warmlink_{device_code}_power_switch
            name: Zasilanie
          - entity: switch.warmlink_{device_code}_h22_switch
            name: Tryb cichy
          - entity: switch.warmlink_{device_code}_h05_switch
            name: Funkcja chłodzenia
          - entity: switch.warmlink_{device_code}_g05_switch
            name: Dezynfekcja
          - entity: switch.warmlink_{device_code}_h01_switch
            name: Pamięć po wyłączeniu

      # Wybory
      - type: entities
        title: Wybory trybu
        entities:
          - entity: select.warmlink_{device_code}_mode_select
            name: Tryb pracy
          - entity: select.warmlink_{device_code}_h07_select
            name: Tryb sterowania
          - entity: select.warmlink_{device_code}_h21_select
            name: Jednostka temperatury
          - entity: select.warmlink_{device_code}_h25_select
            name: Wybór sterowania temp.

      # Temperatury zadane
      - type: entities
        title: Temperatury zadane
        entities:
          - entity: number.warmlink_{device_code}_r01
            name: CWU
          - entity: number.warmlink_{device_code}_r02
            name: Ogrzewanie
          - entity: number.warmlink_{device_code}_r03
            name: Chłodzenie
          - entity: number.warmlink_{device_code}_r70
            name: Temperatura pokojowa

      # CWU
      - type: entities
        title: Zasobnik CWU
        entities:
          - entity: water_heater.warmlink_{device_code}_dhw
            name: Podgrzewacz wody
          - entity: sensor.warmlink_{device_code}_t08
            name: Temperatura zasobnika

      # Wydajność
      - type: entities
        title: Wydajność
        entities:
          - entity: sensor.warmlink_{device_code}_cop_eer_total
            name: COP/EER
          - entity: sensor.warmlink_{device_code}_power_in_total
            name: Pobór mocy
          - entity: sensor.warmlink_{device_code}_capacity_out_total
            name: Moc grzewcza
          - entity: sensor.warmlink_{device_code}_t30
            name: Częstotliwość sprężarki
          - entity: sensor.warmlink_{device_code}_t39
            name: Przepływ wody

  - title: Wykresy
    path: charts
    icon: mdi:chart-line
    cards:
      - type: history-graph
        title: Temperatury (24h)
        hours_to_show: 24
        entities:
          - entity: sensor.warmlink_{device_code}_t01
            name: Wlot
          - entity: sensor.warmlink_{device_code}_t02
            name: Wylot
          - entity: sensor.warmlink_{device_code}_t04
            name: Zewnętrzna
          - entity: sensor.warmlink_{device_code}_t08
            name: Zasobnik

      - type: history-graph
        title: COP (24h)
        hours_to_show: 24
        entities:
          - entity: sensor.warmlink_{device_code}_cop_eer_total
            name: COP/EER

      - type: history-graph
        title: Moc (24h)
        hours_to_show: 24
        entities:
          - entity: sensor.warmlink_{device_code}_power_in_total
            name: Pobór
          - entity: sensor.warmlink_{device_code}_capacity_out_total
            name: Wydajność
'''

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nBrak DEVICE_CODE!")
        print("\nPrzykład użycia:")
        print("  python3 generate_dashboard.py abc123def")
        sys.exit(1)
    
    device_code = sys.argv[1].strip()
    
    # Walidacja
    if len(device_code) < 5:
        print(f"BŁĄD: DEVICE_CODE '{device_code}' wygląda za krótko.")
        print("Sprawdź entity_id w Home Assistant.")
        sys.exit(1)
    
    # Generuj YAML
    dashboard_yaml = TEMPLATE.format(device_code=device_code)
    
    # Zapisz do pliku
    output_file = f"dashboard_{device_code}.yaml"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(dashboard_yaml)
    
    print(f"✅ Wygenerowano: {output_file}")
    print(f"\nTeraz skopiuj zawartość do Home Assistant:")
    print(f"  1. Settings → Dashboards → Add Dashboard")
    print(f"  2. ⋮ → Edit Dashboard → Raw configuration editor")
    print(f"  3. Wklej zawartość {output_file}")
    print(f"  4. Zapisz")

if __name__ == "__main__":
    main()
