# api_client.py - HTTP client for Front API
# reg/api_client.py

import time
from typing import Optional

import requests
from loguru import logger

from .config import API_URL, API_TOKEN, WORKER_ID


class APIClient:
    def __init__(self, base_url: str = API_URL, token: str = API_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.worker_id = WORKER_ID
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Worker-Id": self.worker_id,
        })
        self.session.trust_env = False

    def upload_account(
        self,
        username: str,
        password: str,
        email: str,
        auth_token: Optional[str] = None,
        cookies: str = "",
        retries: int = 3,
    ) -> Optional[dict]:
        url = f"{self.base_url}/api/accounts/upload"
        payload = {
            "username": username,
            "password": password,
            "email": email,
            "auth_token": auth_token or "",
            "cookies": cookies,
        }
        for attempt in range(1, retries + 1):
            try:
                resp = self.session.post(url, json=payload, timeout=15)
                data = resp.json()
                if data.get("code") == 0:
                    return data["data"]
                logger.warning(f"Upload failed for {username}: {data.get('message')}")
                return None
            except requests.RequestException as e:
                logger.warning(f"Upload attempt {attempt}/{retries} failed: {e}")
                if attempt < retries:
                    time.sleep(2)
        return None

    def heartbeat(self, worker_name: str, worker_type: str = "reg") -> bool:
        url = f"{self.base_url}/api/workers/heartbeat"
        try:
            resp = self.session.post(url, json={
                "worker_name": worker_name,
                "worker_type": worker_type,
            }, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False
