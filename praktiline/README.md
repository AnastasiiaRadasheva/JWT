# Praktiline ülesanne: loe, kontrolli, võltsi, ehita

| Fail | Sisu |
|---|---|
| `jwt_harjutus.py` | osad 1–3 (ainult Pythoni standardteek) |
| `app.py` | osa 4, mini-API (Flask + PyJWT) |

```bash
pip install -r requirements.txt
python jwt_harjutus.py
```

## 1. osa: dekodeeri

Päis: `{"alg": "HS256", "typ": "JWT"}`

Payload: `{"sub": "1024", "name": "Mari Maasikas", "role": "student", "iat": 1761206400, "exp": 1761210000}`

| Küsimus | Vastus |
|---|---|
| Algoritm | HS256 |
| Nimi, ID, roll | Mari Maasikas, 1024, student |
| Väljastatud (`iat`) | 23.10.2025 kell 11:00 Tallinna aja järgi |
| Aegub (`exp`) | 23.10.2025 kell 12:00 Tallinna aja järgi |
| Kehtivus | 1 tund |
| Kehtib praegu? | ei, token on aegunud |

## 2. osa: kontrolli allkirja

| Võti | Arvutatud allkiri | Klapib? |
|---|---|---|
| `saladus123` | `ZL6DsKKTa2hRmEkkMASGBI7hZW8ot5bJS2I8oOxVTwM` | jah |
| `saladus124` | `bgjKr0HAIz1RsHpJZcZFu4Mew-tfkM508Mj_J-L7e_s` | ei |

Vale võtmega tuleb täiesti teine allkiri, kuigi võti erineb ühe märgi võrra. Võrdlemiseks kasutan `hmac.compare_digest`, mis võrdleb konstantse ajaga ja kaitseb ajastusrünnakute eest.

## 3. osa: proovi võltsida

- **Kas kontroll õnnestub?** Ei. Allkiri arvutatakse ka payloadi pealt, seega vana allkiri uue payloadiga ei klapi.
- **Mida peaks ründaja teadma?** Salavõtit – siis saaks ta uue payloadi jaoks õige allkirja ise arvutada.
- **Mida see ütleb salavõtme kohta?** Võti peab olema pikk, juhuslik ja hoitud ainult serveris (keskkonnamuutujas), mitte koodis ega GitHubis.

## 4. osa: mini-API

Kasutajad: `adriana` / `adriana123` (student), `anastasiia` / `anastasiia123` (admin).

- `POST /login` – tagastab JWT (`sub`, `name`, `role`, `exp` = 5 min)
- `GET /profiil` – ainult kehtiva tokeniga
- `GET /admin` – ainult `role == "admin"`

`algorithms=["HS256"]` lubab ainult ühe algoritmi (kaitse `alg: none` vastu) ja `jwt.decode` kontrollib ise nii allkirja kui ka `exp` aega.

Käivitamine (PowerShell):

```powershell
$env:JWT_SECRET = "siia-vähemalt-32-märgiline-juhuslik-võti"
python app.py
```

Testimine teises terminalis:

```powershell
$t = (curl.exe -s -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d '{\"username\":\"adriana\",\"password\":\"adriana123\"}' | ConvertFrom-Json).token
curl.exe -i http://127.0.0.1:5000/profiil -H "Authorization: Bearer $t"
curl.exe -i http://127.0.0.1:5000/admin -H "Authorization: Bearer $t"
curl.exe -i http://127.0.0.1:5000/profiil
```

Aegunud tokeni testimiseks: `$env:EXP_SECONDS="10"` enne `python app.py`.

| Test | Vastus |
|---|---|
| `/profiil` kehtiva tokeniga | 200, tokeni andmed |
| `/admin` adriana tokeniga | 403, Õigused puuduvad |
| `/admin` anastasiia tokeniga | 200, Tere, admin anastasiia! |
| `/profiil` ilma tokenita | 401, Token puudub |
| `/profiil` muudetud tokeniga | 401, Vigane token |
| `/profiil` aegunud tokeniga | 401, Token on aegunud |
| `/login` vale parooliga | 401, Vale kasutajanimi või parool |

Kõik juhud on testitud ja annavad oodatud vastuse.

## Lisaülesanne

Server ei pea väljastatud tokenite registrit, vaid kontrollib ainult allkirja ja `exp` aega. Seetõttu kehtib token kuni aegumiseni ka siis, kui kasutaja logis välja või tema konto suleti. Lahendus: lühikese elueaga access token koos refresh tokeniga, mida hoitakse serveris ja saab tühistada. Teine võimalus on blokeerimisnimekiri tühistatud tokenite ID-dega (`jti`).
