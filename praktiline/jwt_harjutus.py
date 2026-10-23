"""Osad 1–3: dekodeeri, kontrolli allkirja, proovi võltsida (ainult standardteek)."""
import base64
import hashlib
import hmac
import json
from datetime import datetime
from zoneinfo import ZoneInfo

TOKEN = ("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
         "eyJzdWIiOiIxMDI0IiwibmFtZSI6Ik1hcmkgTWFhc2lrYXMiLCJyb2xlIjoic3R1ZGVudCIsImlhdCI6MTc2MTIwNjQwMCwiZXhwIjoxNzYxMjEwMDAwfQ."
         "ZL6DsKKTa2hRmEkkMASGBI7hZW8ot5bJS2I8oOxVTwM")


def b64url_decode(tekst):
    return base64.urlsafe_b64decode(tekst + "=" * (-len(tekst) % 4))  # lisame puuduvad =


def b64url_encode(baidid):
    return base64.urlsafe_b64encode(baidid).rstrip(b"=").decode()


def allkirjasta(pais_b64, payload_b64, voti):
    sisend = f"{pais_b64}.{payload_b64}".encode()
    return b64url_encode(hmac.new(voti.encode(), sisend, hashlib.sha256).digest())


pais_b64, payload_b64, allkiri_b64 = TOKEN.split(".")

# 1. osa: dekodeeri
pais = json.loads(b64url_decode(pais_b64))
payload = json.loads(b64url_decode(payload_b64))
tz = ZoneInfo("Europe/Tallinn")
iat = datetime.fromtimestamp(payload["iat"], tz)
exp = datetime.fromtimestamp(payload["exp"], tz)

print("=== 1. osa: dekodeeri ===")
print("Päis:        ", pais)
print("Payload:     ", payload)
print("Väljastatud: ", iat)
print("Aegub:       ", exp)
print("Kehtivus:    ", exp - iat)
print("Kehtib praegu:", datetime.now(tz) < exp)

# 2. osa: kontrolli allkirja (compare_digest võrdleb konstantse ajaga)
print("\n=== 2. osa: kontrolli allkirja ===")
for voti in ["saladus123", "saladus124"]:
    arvutatud = allkirjasta(pais_b64, payload_b64, voti)
    print(f"{voti}: {arvutatud}  klapib: {hmac.compare_digest(arvutatud, allkiri_b64)}")

# 3. osa: proovi võltsida – uus payload, vana allkiri
print("\n=== 3. osa: proovi võltsida ===")
voltsitud_b64 = b64url_encode(json.dumps(dict(payload, role="admin"), separators=(",", ":")).encode())
voltsitud_token = f"{pais_b64}.{voltsitud_b64}.{allkiri_b64}"
print("Võltsitud token:", voltsitud_token)
print("Võltsing läbib kontrolli:",
      hmac.compare_digest(allkirjasta(pais_b64, voltsitud_b64, "saladus123"), allkiri_b64))
print("Salavõtmega saaks ründaja õige allkirja teha:",
      allkirjasta(pais_b64, voltsitud_b64, "saladus123"))
