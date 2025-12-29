#!/usr/bin/env python3
"""
Generator dashboardu Warmlink z podziałem na kategorie.
Zamienia DEVICE_CODE na rzeczywisty kod urządzenia.

Użycie:
    python3 generate_kategoryzowany.py 0c7fedc122c1
"""

import sys
import os

def generate_dashboard(device_code: str):
    """Generuje dashboard z konkretnym kodem urządzenia."""
    
    # Ścieżka do szablonu
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "dashboard_kategoryzowany.yaml")
    output_path = os.path.join(script_dir, f"dashboard_{device_code}_kategoryzowany.yaml")
    
    # Wczytaj szablon
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Zamień DEVICE_CODE
    content = content.replace("DEVICE_CODE", device_code)
    
    # Zapisz wynik
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Dashboard wygenerowany: {output_path}")
    print(f"\n📋 Jak użyć:")
    print(f"1. W Home Assistant: Settings → Dashboards → Add Dashboard")
    print(f"2. Nazwa: 'Pompa Ciepła', Ikona: mdi:heat-pump")
    print(f"3. Otwórz dashboard → ⋮ → Edit → Raw configuration editor")
    print(f"4. Wklej zawartość pliku: {output_path}")
    print(f"5. Zapisz")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Użycie: python3 generate_kategoryzowany.py DEVICE_CODE")
        print("   Przykład: python3 generate_kategoryzowany.py 0c7fedc122c1")
        print("\n   Aby znaleźć DEVICE_CODE:")
        print("   Settings → Devices & Services → Warmlink → kliknij urządzenie")
        print("   Zobacz entity_id np. sensor.0c7fedc122c1_temperatura...")
        sys.exit(1)
    
    device_code = sys.argv[1]
    generate_dashboard(device_code)
