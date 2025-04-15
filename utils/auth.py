# utils/auth.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_jwt_token():
    url = os.getenv("WP_URL") + "/wp-json/jwt-auth/v1/token"
    response = requests.post(url, json={
        "username": os.getenv("WP_USERNAME"),
        "password": os.getenv("WP_PASSWORD")
    })
    response.raise_for_status()
    return response.json()["token"]
