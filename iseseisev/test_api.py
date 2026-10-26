"""Käivitab kõik testjuhud. Server peab töötama ja JWT_SECRET olema sama mis serveril."""
import os
import json
import base64
import datetime
import urllib.request
import urllib.error
import jwt

URL = "http://127.0.0.1:5000"


def call(method, path, token=None, body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def login(username, password):
    return call("POST", "/login", body={"username": username, "password": password})


student = login("adriana", "adriana123")[1]["token"]
admin = login("anastasiia", "anastasiia123")[1]["token"]

# võltsitud token: payloadis role -> admin, allkiri jääb vanaks
h, p, s = student.split(".")
payload = json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)))
payload["role"] = "admin"
p2 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
forged = f"{h}.{p2}.{s}"

# aegunud token (sama võtmega, aga exp on minevikus)
past = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)
expired = jwt.encode({"sub": "adriana", "role": "student", "exp": past},
                     os.environ["JWT_SECRET"], algorithm="HS256")

tests = [
    ("1. Edukas sisselogimine", lambda: login("adriana", "adriana123"), 200),
    ("2. Vale parool", lambda: login("adriana", "vale"), 401),
    ("3. Profiil kehtiva tokeniga", lambda: call("GET", "/profiil", student), 200),
    ("4. Profiil ilma tokenita", lambda: call("GET", "/profiil"), 401),
    ("5. Profiil võltsitud tokeniga", lambda: call("GET", "/profiil", forged), 401),
    ("6. Profiil aegunud tokeniga", lambda: call("GET", "/profiil", expired), 401),
    ("7. Admin student-tokeniga", lambda: call("GET", "/admin", student), 403),
    ("8. Admin admin-tokeniga", lambda: call("GET", "/admin", admin), 200),
    ("9. Admin ilma tokenita", lambda: call("GET", "/admin"), 401),
    ("10. Admin võltsitud tokeniga", lambda: call("GET", "/admin", forged), 401),
    ("11. Admini sisselogimine", lambda: login("anastasiia", "anastasiia123"), 200),
    ("12. Profiil admin-tokeniga", lambda: call("GET", "/profiil", admin), 200),
]

for name, fn, expected in tests:
    code, body = fn()
    result = "LÄBIS" if code == expected else "EI LÄBINUD"
    print(f"{name:35} oodatav {expected}  tegelik {code}  {result}  {body}")
