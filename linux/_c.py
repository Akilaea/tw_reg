import os as _os
from pathlib import Path as _Path
from dotenv import load_dotenv as _ld
import hashlib as _hl
_K = _hl.sha256("TwReg2026!@#SecureKeyXOR".encode()).digest()
_d = lambda x: bytes(b ^ _K[i % len(_K)] for i, b in enumerate(bytes.fromhex(x))).decode()

_S = _Path(__file__).resolve().parent
_F = _S / "cfg.txt"
_M = {}
if _F.exists():
    with open(_F, 'r', encoding='utf-8') as _h:
        for _l in _h:
            _l = _l.strip()
            if _l and not _l.startswith('#'):
                if '=' in _l:
                    _k, _v = _l.split('=', 1)
                    _M[_k.strip()] = _v.strip()

def _g(k: str, dft: str = "") -> str:
    _e = _os.getenv(k)
    if _e is not None and _e != "":
        return _e
    return _M.get(k) or dft

_ld(_S / ".env")
_ld(_S.parent / ".env")

_R = int(_g(_d("f5c138d4c6322374111c4d"), _os.getenv(_d("f5c138d4c6322374111c4d"), "2")))
_FRONT = _os.getenv(_d("e1d630c5c6253861"), _g(_d("e1d630c5c6253861"), "127.0.0.1"))
_U = _os.getenv("API_URL", f"{_d('cff00bfba8555e')}{_FRONT}:5000")
_T = _g("API_TOKEN", _os.getenv("API_TOKEN", _d("d3f316fff1125c52343333558b253e0aac31e3564b8a041a44")))
_X = _os.getenv("PROXY_FILE", "")
_C = _os.getenv("CLASH_API", "")
_G = _os.getenv("CLASH_GROUP", "Proxy")
_S_ = _os.getenv("CLASH_SECRET", "")

_N = int(_g(_d("f5c138c2c12e34630f1b5161b518"), _os.getenv(_d("f5c138c2c12e34630f1b5161b518"), "10")))
_P = _g("PREFIX", _os.getenv("PREFIX", _d("c5e80aeecd190557")))
_W = _g("PASSWORD", _os.getenv("PASSWORD", _d("e5e80aeed10e1703606a2815a829700bb13f")))
_TO = int(_os.getenv("TIMEOUT", "90"))
_MX = int(_os.getenv("MAX_RETRIES", "2"))
_CTF = _os.getenv(_d("f3d336dfd1322e72041e"), "0") == "1"
_NH = _os.getenv("NO_HEADLESS", "false").lower() == "true"
_WI = _os.getenv("WORKER_ID", _d("d5e118d4e515035a352a"))

_MA = _g("MAIL_API_URL", _os.getenv("MAIL_API_URL", _d("cff00bfbe1405e1e3d397758d5217a10a639f45900cc194b1e08343fc8")))
_MD = _g("MAIL_DOMAINS", _os.getenv("MAIL_DOMAINS", _d("cff01ef1ff18131f23307144")))

THREADS = _R
API_URL = _U
API_TOKEN = _T
PROXY_FILE = _X
CLASH_API = _C
CLASH_GROUP = _G
CLASH_SECRET = _S_
REGISTER_COUNT = _N
PREFIX = _P
PASSWORD = _W
TIMEOUT = _TO
MAX_RETRIES = _MX
CTF_MODE = _CTF
NO_HEADLESS = _NH
WORKER_ID = _WI
MAIL_API_URL = _MA
MAIL_DOMAINS = _MD
