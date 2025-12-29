# Copilot Instructions - Warmlink APK Reverse Engineering

## Cel projektu

Analiza APK **Warmlink** (com.phinx.Warmlink v1.4.3) w celu **stworzenia integracji pomp ciepła z Home Assistant**. Aplikacja zarządza urządzeniami grzewczymi Phinx/Aqua Temp przez chmurę.

## ✅ VERIFIED API - Grudzień 2024

### Backend API (ZWERYFIKOWANE)

- **URL API**: `https://cloud.linked-go.com:449/crmservice/api` ⚠️ PORT 449!
- **App ID**: `"16"` (Warmlink-specific)
- **Login Source**: `"IOS"`
- **Area Code**: `"en"`
- **Product ID**: `1501438265440362496` (Warmlink heat pumps)

### Endpointy API (ZWERYFIKOWANE)

```
POST /app/user/login?lang=en          # Logowanie
POST /app/device/deviceList?lang=en   # Lista urządzeń
POST /app/device/getDataByCode?lang=en # Dane urządzenia
POST /app/device/control?lang=en       # Sterowanie
```

### Protocol Codes (ZWERYFIKOWANE)

| Kod   | Opis                              | Przykładowa wartość                     |
| ----- | --------------------------------- | --------------------------------------- |
| Power | Włączone/wyłączone                | "1" / "0"                               |
| Mode  | Tryb pracy                        | "1"=heating, "2"=cooling, "3"=hot_water |
| T01   | Temperatura wlotu                 | "27.1" °C                               |
| T02   | Temperatura wylotu                | "29.4" °C                               |
| T03   | Temperatura zewnętrzna            | "-6.9" °C                               |
| T04   | Temperatura zbiornika             | "1.2" °C                                |
| T05   | Temperatura cewki                 | "-7.0" °C                               |
| R01   | Setpoint wody (zakres 15-70)      | "55.0" °C                               |
| R02   | Setpoint pokojowy (zakres 15-75)  | "30.0" °C                               |
| R03   | Setpoint chłodzenia (zakres 9-28) | "9.0" °C                                |

### Przykład Login Request

```json
POST https://cloud.linked-go.com:449/crmservice/api/app/user/login?lang=en

{
    "userName": "email@example.com",
    "password": "MD5_HASH_HASLA",
    "type": "2",
    "loginSource": "IOS",
    "appId": "16",
    "areaCode": "en"
}
```

### Przykład Response

```json
{
  "error_code": "0",
  "error_msg": "Success",
  "objectResult": {
    "x-token": "token_string...",
    "userId": "your_user_id",
    "appId": "16"
  }
}
```

### Nagłówki dla authenticated requests

```
Content-Type: application/json; charset=utf-8
x-token: <token_z_loginu>
```

### Typy urządzeń (z nazw Activity)

Model IDs zidentyfikowane z `DeviceDetail*Activity`:

- 125, 196, 243, 259, 295, 385, 416, 490, 539, 610, 695, 727, 773
- WindDisk (wentylacja?)

### Parametry pomp ciepła (`res/values/strings.xml`)

Schemat nazewnictwa: `param_{MODEL}_{CATEGORY}{NUMBER}`

- **A** - Temperatury ochronne (A03=Shutdown Ambient, A04=Antifreeze)
- **C** - Sterowanie częstotliwością (C01-C09)
- **D** - Odszranianie (D01-D13)
- **E** - Zawór EEV (E01-E18)
- **F** - Silnik wentylatora (F01-F26)
- **G** - Dezynfekcja wysokotemperaturowa (G01-G05)
- **H** - Konfiguracja systemu (H01-H36)
- **O** - Wyjścia/Outputs (O01-O23)
- **P** - Pompy (P01-P09)
- **R** - Temperatury zadane/setpoints (R01-R46)
- **S** - Ciśnienia (S01+)

### Tryby pracy (`mdl_*` strings)

- `Heating`, `Cooling`, `Hot water`
- `Heating+Hot water`, `Cooling+Hot water`

## Ograniczenia dekompilacji

⚠️ **360 Jiagu Protection** - kod źródłowy zaszyfrowany

- `assets/libjiagu*.so` - loader natywny
- `com.stub.StubApp` - tylko stub widoczny po dekompilacji
- **Rozwiązanie**: analiza ruchu sieciowego (mitmproxy/Charles)

## Rekomendowane podejście dla integracji HA

### 1. Przechwycenie API (priorytet)

```bash
# Uruchom proxy
mitmproxy --mode regular --listen-port 8080

# Skonfiguruj Android emulator/urządzenie do używania proxy
# Zainstaluj certyfikat mitmproxy
```

### 2. Kluczowe endpointy do odkrycia

- `/api/login` lub `/auth/*` - autentykacja
- `/api/devices` - lista urządzeń
- `/api/device/{id}/status` - odczyt stanu
- `/api/device/{id}/control` - sterowanie

### 3. Struktura integracji HA

```
custom_components/warmlink/
├── __init__.py
├── manifest.json
├── config_flow.py      # Login UI
├── api.py              # Klient API cloud.go-heating.com
├── climate.py          # Encja Climate (heating/cooling)
├── water_heater.py     # Hot water tank
└── sensor.py           # Temperatury, COP, błędy
```

## Pliki do analizy

| Plik                      | Informacja                                                |
| ------------------------- | --------------------------------------------------------- |
| `modbus_kaisai_phnix.csv` | **PEŁNE mapowanie rejestrów Modbus RTU** - 635 parametrów |
| `endpoints.txt`           | Lista endpointów API (cloudservice + crmservice)          |
| `res/values/strings.xml`  | Nazwy parametrów, komunikaty błędów                       |
| `res/values/arrays.xml`   | Kody błędów (E003, E032, F00...) z rozwiązaniami          |

## Modbus RTU Mapping (modbus_kaisai_phnix.csv)

**Kluczowe rejestry Read-Write (1xxx):**

| Adres | Kod   | Opis                | Zakres                                     |
| ----- | ----- | ------------------- | ------------------------------------------ |
| 1011  | Power | Włącz/Wyłącz        | 0-1                                        |
| 1012  | Mode  | Tryb pracy          | 0=HW, 1=Heating, 2=Cooling, 3=HW+H, 4=HW+C |
| 1157  | R01   | DHW Target Temp     | R36-R37°C                                  |
| 1158  | R02   | Heating Target Temp | R10-R11°C                                  |
| 1159  | R03   | Cooling Target Temp | R08-R09°C                                  |
| 1239  | R70   | Room Target Temp    | 5-27°C                                     |

**Kluczowe rejestry Read-Only (2xxx):**

| Adres | Kod                 | Opis                                         |
| ----- | ------------------- | -------------------------------------------- |
| 2011  | Power State         | Stan zasilania                               |
| 2012  | ModeState           | 0=Cool, 1=Heat, 2=Defrost, 3=Disinfect, 4=HW |
| 2045  | T01                 | Inlet Water Temp                             |
| 2046  | T02                 | Outlet Water Temp                            |
| 2047  | T08                 | DHW Tank Temp                                |
| 2048  | T04                 | Ambient Temp (AT)                            |
| 2054  | Power In(Total)     | Pobór mocy kW                                |
| 2059  | Capacity Out(Total) | Moc grzewcza kW                              |
| 2060  | COP/EER(Total)      | Współczynnik wydajności                      |
| 2071  | T30                 | Częstotliwość sprężarki Hz                   |
| 2077  | T39                 | Przepływ wody L/min                          |

**Dodatkowe pliki referencyjne:**

| Plik                      | Informacja                          |
| ------------------------- | ----------------------------------- |
| `res/8G.xml`              | network_security_config             |
| `AndroidManifest.xml`     | Deep links, permissions, activities |
| `assets/AAChartView.html` | Wykresy COP/Heating Capacity        |

## Przydatne komendy

```bash
# Szukaj URL-i w strings
grep -i "url\|http\|api" res/values/strings.xml

# Lista parametrów dla modelu 196
grep "param_196" res/values/strings.xml

# Kody błędów
grep -E "^E[0-9]|^F[0-9]" res/values/arrays.xml
```

## Uwagi dla AI agentów

1. **Nie próbuj budować APK** - to reverse engineering, nie development
2. **Priorytet**: analiza ruchu sieciowego > dekompilacja
3. **strings.xml** jest głównym źródłem wiedzy o API
4. Model 196 ma najobszerniejszą dokumentację parametrów
5. Push notifications przez GeTui - może być potrzebne do real-time updates

---

## Integracja Home Assistant (custom_components/warmlink/)

**STATUS: GOTOWA DO TESTÓW** ✅

Integracja HA znajduje się w `custom_components/warmlink/`.

### Struktura plików

| Plik               | Opis                                      |
| ------------------ | ----------------------------------------- |
| `__init__.py`      | Setup integracji, ładowanie platform      |
| `api.py`           | Klient API (ZWERYFIKOWANY)                |
| `const.py`         | Stałe API, protocol codes (ZWERYFIKOWANE) |
| `config_flow.py`   | UI logowania w HA                         |
| `coordinator.py`   | DataUpdateCoordinator dla polling         |
| `climate.py`       | Encja Climate (heating/cooling)           |
| `sensor.py`        | Sensory temperatury T01-T05, R01-R03      |
| `binary_sensor.py` | Status online, power, awarie              |
| `water_heater.py`  | Podgrzewacz wody                          |
| `translations/`    | Tłumaczenia en/pl                         |

### Status implementacji

✅ **ZWERYFIKOWANE I ZAIMPLEMENTOWANE**:

- Login przez email/hasło (MD5 hash, userName, appId=16)
- Pobieranie listy urządzeń (deviceList z productId)
- Pobieranie danych (getDataByCode z protocalCodes)
- Climate entity z HVAC modes (Power, Mode)
- Sensory temperatury (T01-T05, R01-R03)
- Binary sensory (online, power, fault)
- Water heater entity

### Instalacja w Home Assistant

1. Skopiuj folder `custom_components/warmlink/` do instalacji HA
2. Restart Home Assistant
3. Dodaj integrację: Settings → Integrations → Add → Warmlink
4. Podaj email i hasło z aplikacji Warmlink

### Testowanie API

```bash
# Test połączenia z API
python3 test_warmlink_verified.py EMAIL HASŁO

# Przykład
python3 test_warmlink_verified.py user@example.com mojehaslo123
```

### Rozwiązywanie problemów

**SSL Certificate errors**: API na porcie 449 może mieć problemy z certyfikatem.
Kod używa `ssl=False` w aiohttp dla obejścia.

**Brak urządzeń**: Upewnij się, że używasz konta z aplikacji Warmlink (nie Aqua Temp).
Warmlink wymaga `appId: "16"`.

### Referencje

- GitHub Issue: [radical-squared/aquatemp#99](https://github.com/radical-squared/aquatemp/issues/99) - "Heatpumps - warmlink support"
- Warmlink używa tego samego backendu co Aqua Temp, ale z innym `appId`
