import os
from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)

SECRET = os.environ["JWT_SECRET"]  # salavõti tuleb keskkonnamuutujast
ALGORITHM = "HS256"                # lubatud ainult üks algoritm
EXP_SECONDS = int(os.environ.get("EXP_SECONDS", 300))  # vaikimisi 5 minutit

# testkasutajad (paroolid võivad olla nähtavad)
USERS = {
    "adriana": {"password": "adriana123", "id": "1", "role": "student"},
    "anastasiia": {"password": "anastasiia123", "id": "2", "role": "admin"},
}


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = USERS.get(data.get("username"))
    if not user or user["password"] != data.get("password"):
        return jsonify(error="Vale kasutajanimi või parool"), 401

    payload = {
        "sub": user["id"],
        "name": data["username"],
        "role": user["role"],
        "exp": datetime.now(timezone.utc) + timedelta(seconds=EXP_SECONDS),
    }
    return jsonify(token=jwt.encode(payload, SECRET, algorithm=ALGORITHM)), 200


def requires_token(role=None):
    """Kontrollib tokenit; vea korral 401, vale rolli korral 403."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify(error="Token puudub"), 401
            try:
                data = jwt.decode(auth[len("Bearer "):], SECRET, algorithms=[ALGORITHM])
            except jwt.ExpiredSignatureError:
                return jsonify(error="Token on aegunud"), 401
            except jwt.InvalidTokenError:
                return jsonify(error="Vigane token"), 401
            if role and data.get("role") != role:
                return jsonify(error="Õigused puuduvad"), 403
            return f(data, *args, **kwargs)
        return wrapper
    return decorator


@app.get("/profiil")
@requires_token()
def profiil(data):
    return jsonify(data), 200


@app.get("/admin")
@requires_token(role="admin")
def admin(data):
    return jsonify(message=f"Tere, admin {data['name']}!"), 200


if __name__ == "__main__":
    app.run(port=5000)
