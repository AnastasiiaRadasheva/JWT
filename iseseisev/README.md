# Iseseisev töö: JWT mini-API (Flask + PyJWT)

Notioni lehe tekst: `NOTION.md`.

Lõpp-punktid:

| Meetod | Tee | Kirjeldus |
|---|---|---|
| POST | `/login` | võtab `username` ja `password`, tagastab JWT (`sub`, `role`, `exp` = 5 min) |
| GET | `/profiil` | ainult kehtiva tokeniga, tagastab tokeni andmed |
| GET | `/admin` | ainult kui `role == "admin"` |

Vead: puuduv/vigane/aegunud token → **401**, õigused puuduvad → **403**.

Testkasutajad:

| Kasutaja | Parool | Roll |
|---|---|---|
| adriana | adriana123 | student |
| anastasiia | anastasiia123 | admin |

## Käivitamine

```bash
pip install -r requirements.txt
```

Salavõti antakse keskkonnamuutujaga `JWT_SECRET` (koodis seda pole).

Windows PowerShell:

```powershell
$env:JWT_SECRET = "mingi-pikk-juhuslik-salavõti"
python app.py
```

Linux / macOS / Git Bash:

```bash
export JWT_SECRET="mingi-pikk-juhuslik-salavõti"
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
