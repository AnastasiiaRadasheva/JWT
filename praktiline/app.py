import os
import datetime
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)

SECRET = os.environ["JWT_SECRET"]  # salavõti tuleb keskkonnamuutujast
ALGORITHM = "HS256"                # lubatud ainult üks algoritm
EXP_SECONDS = int(os.environ.get("EXP_SECONDS", 300))  # vaikimisi 5 minutit

# testkasutajad (paroolid võivad olla nähtavad)
USERS = {
    "adriana": {"password": "adriana123", "role": "student"},
    "anastasiia": {"password": "anastasiia123", "role": "admin"},
}


def get_token_data():
    """Tagastab tokeni sisu või None, kui token puudub või on vigane."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[len("Bearer "):]
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:  # vale allkiri, aegunud, vigane vorming
        return None


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = USERS.get(data.get("username"))
    if not user or user["password"] != data.get("password"):
        return jsonify(error="Vale kasutajanimi või parool"), 401

    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        "sub": data["username"],
        "role": user["role"],
        "iat": now,
        "exp": now + datetime.timedelta(seconds=EXP_SECONDS),
    }
    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return jsonify(token=token), 200


@app.get("/profiil")
def profiil():
    data = get_token_data()
    if data is None:
        return jsonify(error="Token puudub või on vigane"), 401
    return jsonify(data), 200


@app.get("/admin")
def admin():
    data = get_token_data()
    if data is None:
        return jsonify(error="Token puudub või on vigane"), 401
    if data.get("role") != "admin":
        return jsonify(error="Pole piisavalt õigusi"), 403
    return jsonify(message=f"Tere, admin {data['sub']}!"), 200


if __name__ == "__main__":
    app.run(port=5000)
