# config.py - Configuration for registration client
# reg/config.py

import os
from pathlib import Path

from dotenv import load_dotenv

_self_dir = Path(__file__).resolve().parent
load_dotenv(_self_dir / ".env")
load_dotenv(_self_dir.parent / ".env")

THREADS = int(os.getenv("REG_THREADS", "5"))
API_URL = os.getenv("API_URL", "http://127.0.0.1:5000")
API_TOKEN = os.getenv("API_TOKEN", "twitch-cdk-api-token-2024")
PROXY_FILE = os.getenv("PROXY_FILE", "")
CLASH_API = os.getenv("CLASH_API", "")
CLASH_GROUP = os.getenv("CLASH_GROUP", "Proxy")
CLASH_SECRET = os.getenv("CLASH_SECRET", "")

REGISTER_COUNT = int(os.getenv("REGISTER_COUNT", "10"))
PREFIX = os.getenv("PREFIX", "blue_ctf")
PASSWORD = os.getenv("PASSWORD", "BlueCtf2026!Secure")
TIMEOUT = int(os.getenv("TIMEOUT", "90"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
CTF_MODE = os.getenv("TWITCH_CTF", "0") == "1"
NO_HEADLESS = os.getenv("NO_HEADLESS", "false").lower() == "true"
WORKER_ID = os.getenv("WORKER_ID", "reg_worker")

MAIL_API_URL = os.getenv("MAIL_API_URL", "https://mailapi.izlvxhe.cn")
MAIL_ADMIN_AUTH = os.getenv("MAIL_ADMIN_AUTH", "Aalcsttkx1!")
MAIL_DOMAINS = os.getenv("MAIL_DOMAINS", "")
