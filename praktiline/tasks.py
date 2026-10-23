"""Osad 4–6: dekodeeri, kontrolli allkirja, proovi võltsida."""
import json
import hmac
import base64
import hashlib
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

TOKEN = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
         "eyJzdWIiOiIxMDI0IiwibmFtZSI6Ik1hcmkgTWFhc2lrYXMiLCJyb2xlIjoic3R1ZGVudCIsImlhdCI6MTc2MTIwNjQwMCwiZXhwIjoxNzYxMjEwMDAwfQ."
         "ZL6DsKKTa2hRmEkkMASGBI7hZW8ot5bJS2I8oOxVTwM")


def b64decode(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))  # lisame puuduvad =


def b64encode(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def sign(header_b64, payload_b64, key):
    msg = (header_b64 + "." + payload_b64).encode()
    return b64encode(hmac.new(key.encode(), msg, hashlib.sha256).digest())


header_b64, payload_b64, signature = TOKEN.split(".")

print("=== 4. osa: dekodeeri ===")
header = json.loads(b64decode(header_b64))
payload = json.loads(b64decode(payload_b64))
print("Päis:   ", header)
print("Payload:", payload)

tallinn = ZoneInfo("Europe/Tallinn")
iat = datetime.fromtimestamp(payload["iat"], tallinn)
exp = datetime.fromtimestamp(payload["exp"], tallinn)
print("Väljastatud:", iat)
print("Aegub:      ", exp)
print("Kehtivus:   ", exp - iat)
now = datetime.now(timezone.utc).timestamp()
print("Kehtib praegu:", "jah" if now < payload["exp"] else "ei, on aegunud")

print("\n=== 5. osa: kontrolli allkirja ===")
for key in ["saladus123", "saladus124"]:
    s = sign(header_b64, payload_b64, key)
    print(f"{key}: {s}  ->  {'KLAPIB' if s == signature else 'EI KLAPI'}")

print("\n=== 6. osa: proovi võltsida ===")
payload["role"] = "admin"
forged_payload_b64 = b64encode(json.dumps(payload, separators=(",", ":")).encode())
forged = f"{header_b64}.{forged_payload_b64}.{signature}"
print("Võltsitud token:", forged)
ok = sign(header_b64, forged_payload_b64, "saladus123") == signature
print("Allkirja kontroll:", "õnnestus" if ok else "EBAÕNNESTUS (allkiri ei klapi uue payloadiga)")
print("Kui ründaja teab salavõtit, saab ta õige allkirja ise arvutada:")
print(f"{header_b64}.{forged_payload_b64}.{sign(header_b64, forged_payload_b64, 'saladus123')}")
