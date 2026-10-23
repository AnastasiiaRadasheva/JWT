# Praktiline ülesanne: loe, kontrolli, võltsi, ehita

Antud token (HS256, salavõti `saladus123`):

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDI0IiwibmFtZSI6Ik1hcmkgTWFhc2lrYXMiLCJyb2xlIjoic3R1ZGVudCIsImlhdCI6MTc2MTIwNjQwMCwiZXhwIjoxNzYxMjEwMDAwfQ.ZL6DsKKTa2hRmEkkMASGBI7hZW8ot5bJS2I8oOxVTwM
```

Osad 4–6 käivituvad käsuga:

```bash
pip install -r requirements.txt
python tasks.py
```

## 4. osa: dekodeeri

Päis: `{"alg": "HS256", "typ": "JWT"}`

Payload: `{"sub": "1024", "name": "Mari Maasikas", "role": "student", "iat": 1761206400, "exp": 1761210000}`

| Küsimus | Vastus |
|---|---|
| Algoritm | HS256 |
| Nimi, ID, roll | Mari Maasikas, 1024, student |
| Väljastatud (`iat`) | 23.10.2025 kell 11:00 Tallinna aja järgi |
| Aegub (`exp`) | 23.10.2025 kell 12:00 Tallinna aja järgi |
| Kui kaua kehtib | 1 tund (3600 sekundit) |
| Kas kehtib praegu | Ei, token on aegunud |

## 5. osa: kontrolli allkirja

| Võti | Arvutatud allkiri | Tulemus |
|---|---|---|
| `saladus123` | `ZL6DsKKTa2hRmEkkMASGBI7hZW8ot5bJS2I8oOxVTwM` | klapib tokeni kolmanda osaga |
| `saladus124` | `bgjKr0HAIz1RsHpJZcZFu4Mew-tfkM508Mj_J-L7e_s` | ei klapi |

Vale võtmega tuleb täiesti teine allkiri, kuigi võti erineb ainult ühe märgi võrra. Server lükkaks sellise tokeni tagasi.

## 6. osa: proovi võltsida

`"role":"student"` muudeti `"role":"admin"`-iks ja pandi kokku vana allkirjaga:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDI0IiwibmFtZSI6Ik1hcmkgTWFhc2lrYXMiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3NjEyMDY0MDAsImV4cCI6MTc2MTIxMDAwMH0.ZL6DsKKTa2hRmEkkMASGBI7hZW8ot5bJS2I8oOxVTwM
```

- **Kas allkirja kontroll õnnestub?** Ei.
- **Miks?** Allkiri arvutatakse päise ja payloadi põhjal. Kui payload muutub, peab muutuma ka allkiri, aga vana allkiri vastab vanale payloadile.
- **Mida peaks ründaja teadma?** Salavõtit. Siis saab ta uue payloadi jaoks õige allkirja ise arvutada (`tasks.py` näitab seda viimasel real).
- **Mida see ütleb salavõtme kohta?** Kogu turvalisus sõltub võtmest. See peab olema pikk, juhuslik ja salajane: mitte koodis, mitte GitHubis, vaid keskkonnamuutujas.

## 7. osa: mini-API

`app.py`: Flask + PyJWT, kasutajad `adriana` (student) ja `anastasiia` (admin).

- `POST /login` tagastab JWT, milles on `sub`, `role` ja `exp` (5 minutit).
- `GET /profiil` töötab ainult kehtiva tokeniga ja tagastab tokeni andmed.
- `GET /admin` töötab ainult siis, kui `role == "admin"`.

Käivitamine (PowerShell):

```powershell
$env:JWT_SECRET = "pikk-juhuslik-võti"
python app.py
```

Testimine curl-iga (teises terminalis):

| Test | Käsk | Oodatav |
|---|---|---|
| Kehtiv token | `curl.exe -i http://127.0.0.1:5000/profiil -H "Authorization: Bearer TOKEN"` | 200 |
| Puuduv token | `curl.exe -i http://127.0.0.1:5000/profiil` | 401 |
| Muudetud token | sama käsk võltsitud tokeniga | 401 |
| Aegunud token | `$env:EXP_SECONDS="10"` serveris, oodata 15 s | 401 |
| Student `/admin`-is | `curl.exe -i http://127.0.0.1:5000/admin -H "Authorization: Bearer TOKEN"` | 403 |

Tokeni saamine:

```powershell
curl.exe -i -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d '{\"username\":\"adriana\",\"password\":\"adriana123\"}'
```

## Lisaülesanne

JWT-d on raske enne aegumist tühistada, sest server ei hoia väljastatud tokeneid kuskil meeles. Ta kontrollib ainult allkirja ja aegumisaega, seega kehtib õige allkirjaga token kuni `exp` hetkeni. Isegi kui kasutaja logib välja või tema konto suletakse, saab vana tokeniga edasi päringuid teha. Lahendus: anda väga lühikese elueaga access token (nt 5–15 minutit) koos refresh tokeniga, mida hoitakse serveris ja mida saab igal hetkel tühistada. Teine võimalus on blokeerimisnimekiri, kuhu pannakse tühistatud tokenite ID-d (`jti`).
