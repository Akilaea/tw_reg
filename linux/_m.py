import asyncio as _a
import os as _o
import subprocess as _sp
import sys as _sy
from pathlib import Path as _P
from loguru import logger as _L
import hashlib as _hl
_K = _hl.sha256("TwReg2026!@#SecureKeyXOR".encode()).digest()
_d = lambda x: bytes(b ^ _K[i % len(_K)] for i, b in enumerate(bytes.fromhex(x))).decode()

from ._c import THREADS, REGISTER_COUNT, PREFIX, PASSWORD, TIMEOUT, MAX_RETRIES, NO_HEADLESS, CTF_MODE, MAIL_DOMAINS
from ._n import APIClient
from ._h import register_account

def _xv():
    if _o.environ.get("DISPLAY") == ":99":
        return
    try:
        _r = _sp.run(["pgrep", "-f", "Xvfb :99"], capture_output=True, text=True)
        if _r.returncode == 0 and _r.stdout.strip():
            _o.environ["DISPLAY"] = ":99"
            return
    except Exception:
        pass
    try:
        _sp.Popen(["Xvfb", ":99", "-screen", "0", "1920x1080x24"],
                  stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
        _o.environ["DISPLAY"] = ":99"
        _L.info("Xvfb started on :99 (1920x1080x24)")
    except FileNotFoundError:
        _L.warning("Xvfb not found. Install: sudo apt install -y xvfb")
    except Exception as _e:
        _L.warning(f"Xvfb start failed: {_e}")

_L.remove()
_lv = _o.environ.get(_d("ebcb38dec02f2e7d150e5b78"), _o.environ.get(_d("e3c13dded5"), "false").lower() == "true" and _d("e3c13dded5") or _d("eeca39c4"))
_L.add(_sy.stderr, format=_d("9be30deef7144f4a24317351c1154a279a77cb754bfc7008386e6037d1257155dab850ece01f145f6e786214c7207608a636b8430add424d1c1c7a6684623e09cbe109eefe44514d706472518d297f40b837e34b15d9534d0d1a7536d969674a99"), level=_lv)
_L.add(_P(__file__).parent / f"{_d('d5e118d4fe131f442807')}{{time:YYYY-MM-DD}}.log", rotation=_d("96b45fc6d0"), retention=_d("90a41beaeb09"), level=_d("e3c13dded5"))
_o.environ[_d("f3d336dfd1322e72041e")] = "1" if CTF_MODE else "0"

async def _rr(idx: int, ac) -> None:
    try:
        from cloakbrowser import launch_async
    except ImportError:
        _L.error("cloakbrowser not installed. Run: pip install cloakbrowser")
        return
    _L.info(f"[{idx}] {_d('ebe50ae5f112185f37787c46943b601bb17aae5c0fca514b040f')}")
    _br = None
    _cx = None
    try:
        _xv()
        _br = await _a.wait_for(launch_async(headless=False, humanize=True), timeout=30)
        _cx = await _br.new_context(viewport={"width": 1920, "height": 1080}, locale="en_US")
        _L.debug(f"[{idx}] {_d('e5f610fce11f03113c396b5a9824761ae315cd')}")
        _pg = await _cx.new_page()
        _L.debug(f"[{idx}] {_d('f7e518eeb2081450342132148838720cb733e85f46ca514f19552e28dd6b6b49c9')}")
        _rs = await register_account(idx=idx, ctx=_cx, page=_pg, pf=PREFIX, pw=PASSWORD, to=TIMEOUT, mr=MAX_RETRIES, dm=MAIL_DOMAINS)
        if _rs.get(_d("d4f01effe709")) == _d("d4f11ce8f70902"):
            _up = ac._p(u=_rs["username"], w=_rs["password"], e=_rs.get("email", ""), a=_rs.get("auth_token", ""), c=_rs.get("cookies", ""))
            if _up:
                _L.info(f"[{idx}] {_rs['username']} - {_d('d2f413e4f31e1455702c7114ba1c5a')}")
            else:
                _L.warning(f"[{idx}] {_rs['username']} - {_d('e6d436abe70a1d5e313c3e529a257f1ba7')}")
        else:
            _L.warning(f"[{idx}] {_d('f5e118e2e10e03502431715adb2a7217af3fe2')}: {_rs.get(_d('c2f60de4e0'))}")
        return _rs
    except _a.TimeoutError:
        _L.error(f"[{idx}] {_d('e5f610fce11f03113c396b5a9824330aaa37e35713cc')}")
    except Exception as _e:
        _L.error(f"[{idx}] {_d('e5f610fce11f0311352a6c5b89')}: {_e}")
    finally:
        if _cx:
            try:
                await _cx.close()
            except Exception:
                pass
        if _br:
            try:
                await _br.close()
            except Exception:
                pass
    return {_d("d4f01effe709"): _d("c1e516e7f71e"), _d("c2f60de4e0"): _d("c5f610fce11f0311352a6c5b896c7c0ce33ffe5b03c840411f48")}

async def _mn() -> None:
    _ac = APIClient()
    _L.info(f"{_d('f4f01ef9e6131f56702a7b53923f670ca22eef5708')}: {REGISTER_COUNT} {_d('c6e71ce4e71405427c')} {THREADS} {_d('d3ec0deef31e021d703c77469e2f675ead3ff24f09ca5f')}")
    _sm = _a.Semaphore(THREADS)
    _cp = 0
    _fc = 0
    _lk = _a.Lock()
    _ft = int(_o.getenv(_d("e1c536c7c728346e04104c71a8045c3287"), "5"))
    _ts = []

    async def _ro(i: int) -> None:
        nonlocal _cp, _fc, _ts
        async with _sm:
            _ac._h(_d("d5e118d4e515035a352a"), _d("d5e118"))
            try:
                _rs = await _rr(i, _ac)
            except _a.CancelledError:
                _L.warning(f"[{i}] {_d('f3e50ce0b219105f333d72589e28')}")
                return
            async with _lk:
                _cp += 1
                if not _rs or _rs.get(_d("d4f01effe709")) != _d("d4f11ce8f70902"):
                    _fc += 1
                _L.info(f"{_d('f7f610ece01f02426a')} {_cp}/{REGISTER_COUNT} ({_d('c1e516e7e70814426a')} {_fc})")
                if _fc >= _ft:
                    _L.error(f"{_d('e1e516e7e708141124306c5188247c12a77af45d07db5c4d14')} ({_fc}), {_d('c4e511e8f7161d583e3f3e469e217217ad33e85f46cc555b1b55')}")
                    for _t in _ts:
                        if not _t.done():
                            _t.cancel()

    _ts = [_a.create_task(_ro(i)) for i in range(REGISTER_COUNT)]
    await _a.gather(*_ts, return_exceptions=True)
    _ac._h(_d("d5e118d4e515035a352a"), _d("d5e118"))
    _L.info(f"{_d('f5e118e2e10e03502431715adb2f7c13b336e34c0396')} {REGISTER_COUNT} {_d('c6e71ce4e714054270396a409e21630aa63ea8')}")

def entry():
    _a.run(_mn())

if __name__ == "__main__":
    entry()
