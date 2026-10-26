# Iseseisev töö: JWT mini-API (Flask + PyJWT)

Notioni leht: [JWT – Anastasiia](https://app.notion.com/p/JWT-Anastasiia-402b3d43c5be8060b5bcf719d6501415)

Lõpp-punktid:

| Meetod | Tee | Kirjeldus |
|---|---|---|
| POST | `/login` | võtab `username` ja `password`, tagastab JWT (`sub`, `name`, `role`, `exp` = 5 min) |
| GET | `/profiil` | ainult kehtiva tokeniga, tagastab tokeni andmed |
| GET | `/admin` | ainult kui `role == "admin"` |

Vead: `Token puudub`, `Vigane token`, `Token on aegunud` → **401**, `Õigused puuduvad` → **403**.

Testkasutajad:

| Kasutaja | Parool | Roll |
|---|---|---|
| adriana | adriana123 | student |
| anastasiia | anastasiia123 | admin |

## Käivitamine

```bash
pip install -r requirements.txt
```

Salavõti antakse keskkonnamuutujaga `JWT_SECRET` (koodis seda pole). Võti peab olema vähemalt 32 tähemärki, muidu PyJWT annab hoiatuse. Juhusliku võtme saab nii:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Windows PowerShell:

```powershell
$env:JWT_SECRET = "siia-genereeritud-võti"
python app.py
```

Linux / macOS / Git Bash:

```bash
export JWT_SECRET="siia-genereeritud-võti"
python app.py
```

Server käivitub aadressil `http://127.0.0.1:5000`.

Aegunud tokeni testimiseks saab kehtivust lühendada: `EXP_SECONDS=10`.

## Testimine curl-iga

```bash
# sisselogimine
curl -i -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d "{\"username\":\"adriana\",\"password\":\"adriana123\"}"

# profiil (asenda TOKEN)
curl -i http://127.0.0.1:5000/profiil -H "Authorization: Bearer TOKEN"

# admin
curl -i http://127.0.0.1:5000/admin -H "Authorization: Bearer TOKEN"
```

Kõik testjuhud korraga: `python test_api.py` (server peab töötama, `JWT_SECRET` peab olema sama).
