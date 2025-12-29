#!/usr/bin/env python3
"""
Test skrypt do sprawdzenia endpointów urządzeń udostępnionych.

Użycie:
    python3 test_shared_devices.py EMAIL HASŁO

Testuje różne warianty endpointów:
1. crmservice/api/app/device/getAuthDeviceList
2. crmservice/api/device/getAuthDeviceList  
3. cloudservice/api/device/getAuthDeviceList
"""

import sys
import json
import hashlib
import urllib.request
import urllib.error
import ssl

# API configuration
API_BASE_CRM = "https://cloud.linked-go.com:449/crmservice/api"
API_BASE_CLOUD = "https://cloud.linked-go.com:449/cloudservice/api"
APP_ID = "16"
LOGIN_SOURCE = "IOS"
AREA_CODE = "en"


def md5_hash(password: str) -> str:
    """Hash password with MD5."""
    return hashlib.md5(password.encode()).hexdigest()


def create_ssl_context():
    """Create SSL context that ignores cert verification."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def post_request(url: str, data: dict, headers: dict = None) -> dict:
    """Send POST request and return JSON response."""
    if headers is None:
        headers = {}
    
    headers["Content-Type"] = "application/json; charset=utf-8"
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers=headers,
        method="POST"
    )
    
    try:
        ctx = create_ssl_context()
        resp = urllib.request.urlopen(req, context=ctx, timeout=30)
        return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": str(e), "code": e.code, "body": body}
    except Exception as e:
        return {"error": str(e)}


def login(email: str, password: str) -> dict:
    """Login to Warmlink API."""
    url = f"{API_BASE_CRM}/app/user/login?lang={AREA_CODE}"
    password_md5 = md5_hash(password)
    
    data = {
        "userName": email,
        "password": password_md5,
        "type": "2",
        "loginSource": LOGIN_SOURCE,
        "appId": APP_ID,
        "areaCode": AREA_CODE,
    }
    
    print(f"\n{'='*60}")
    print("LOGIN")
    print(f"{'='*60}")
    print(f"URL: {url}")
    
    result = post_request(url, data)
    
    if result.get("error_msg") == "Success":
        token = result.get("objectResult", {}).get("x-token")
        user_id = result.get("objectResult", {}).get("userId")
        print(f"✅ Login OK! user_id={user_id}")
        return {"token": token, "user_id": user_id}
    else:
        print(f"❌ Login failed: {result}")
        return {}


def test_endpoint(name: str, url: str, data: dict, headers: dict) -> dict:
    """Test an endpoint and print results."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    result = post_request(url, data, headers)
    
    error_msg = result.get("error_msg", result.get("error", ""))
    error_code = result.get("error_code", "")
    
    if error_msg == "Success":
        devices = result.get("objectResult", [])
        print(f"✅ Success! Found {len(devices)} devices")
        for i, dev in enumerate(devices):
            code = dev.get("device_code") or dev.get("deviceCode") or "?"
            name = dev.get("device_nick_name") or dev.get("deviceNickName") or code
            status = dev.get("deviceStatus") or dev.get("device_status") or "?"
            print(f"   {i+1}. {name} ({code}) - {status}")
        return result
    else:
        print(f"❌ Failed: {error_msg} (code: {error_code})")
        if "body" in result:
            print(f"   Body: {result['body'][:200]}")
        return result


def main():
    if len(sys.argv) < 3:
        print("Użycie: python3 test_shared_devices.py EMAIL HASŁO")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    # Login
    login_result = login(email, password)
    if not login_result.get("token"):
        print("\n❌ Nie można się zalogować!")
        sys.exit(1)
    
    token = login_result["token"]
    user_id = login_result.get("user_id", "")
    headers = {"x-token": token}
    
    # Test data variants
    data_variants = [
        {"appId": APP_ID},
        {"appId": APP_ID, "userId": user_id},
        {"appId": APP_ID, "type": "1"},  # type może mieć znaczenie
        {"appId": APP_ID, "userId": user_id, "pageSize": 100, "pageNum": 1},
    ]
    
    # Endpoints to test
    endpoints = [
        # CRM service endpoints
        ("CRM: app/device/deviceList", f"{API_BASE_CRM}/app/device/deviceList?lang={AREA_CODE}"),
        ("CRM: app/device/getAuthDeviceList", f"{API_BASE_CRM}/app/device/getAuthDeviceList?lang={AREA_CODE}"),
        ("CRM: device/getAuthDeviceList", f"{API_BASE_CRM}/device/getAuthDeviceList?lang={AREA_CODE}"),
        # Cloud service endpoints
        ("CLOUD: device/getAuthDeviceList", f"{API_BASE_CLOUD}/device/getAuthDeviceList?lang={AREA_CODE}"),
        ("CLOUD: app/device/getAuthDeviceList", f"{API_BASE_CLOUD}/app/device/getAuthDeviceList?lang={AREA_CODE}"),
    ]
    
    print(f"\n{'#'*60}")
    print("TESTOWANIE ENDPOINTÓW URZĄDZEŃ UDOSTĘPNIONYCH")
    print(f"{'#'*60}")
    print(f"Email: {email}")
    print(f"User ID: {user_id}")
    
    results = {}
    
    for endpoint_name, url in endpoints:
        # Test with basic data first
        data = {"appId": APP_ID}
        result = test_endpoint(endpoint_name, url, data, headers)
        results[endpoint_name] = result
        
        # If failed, try with userId
        if result.get("error_msg") != "Success" and user_id:
            data_with_user = {"appId": APP_ID, "userId": user_id}
            result2 = test_endpoint(f"{endpoint_name} (z userId)", url, data_with_user, headers)
            results[f"{endpoint_name} (z userId)"] = result2
    
    # Summary
    print(f"\n{'#'*60}")
    print("PODSUMOWANIE")
    print(f"{'#'*60}")
    
    working = []
    for name, result in results.items():
        if result.get("error_msg") == "Success":
            devices = result.get("objectResult", [])
            working.append((name, len(devices)))
    
    if working:
        print("\n✅ Działające endpointy:")
        for name, count in working:
            print(f"   - {name}: {count} urządzeń")
    else:
        print("\n❌ Żaden endpoint nie zwrócił urządzeń")
        print("\nMożliwe przyczyny:")
        print("   1. Konto nie ma żadnych urządzeń (własnych ani udostępnionych)")
        print("   2. Urządzenia są powiązane z innym appId (nie Warmlink)")
        print("   3. Token wygasł")


if __name__ == "__main__":
    main()
