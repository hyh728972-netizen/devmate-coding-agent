import time

import jwt


def generate_token(api_key: str, exp_seconds: int = 3600) -> str:
    key_id, key_secret = api_key.split(".")
    now = int(round(time.time()))
    payload = {
        "api_key": key_id,
        "exp": now + exp_seconds * 1000,
        "timestamp": now,
    }
    return jwt.encode(
        payload,
        key_secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )
