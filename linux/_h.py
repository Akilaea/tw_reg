import asyncio as _a
import json as _j
import time as _t
from pathlib import Path as _P
from typing import Optional as _O
from loguru import logger as _L
from ._c import PREFIX, PASSWORD, TIMEOUT, MAX_RETRIES, CTF_MODE, MAIL_API_URL, MAIL_DOMAINS
import hashlib as _hl
_K = _hl.sha256("TwReg2026!@#SecureKeyXOR".encode()).digest()
_d = lambda x: bytes(b ^ _K[i % len(_K)] for i, b in enumerate(bytes.fromhex(x))).decode()
try:
    import requests as _rq
    from urllib3 import disable_warnings as _dw
    _dw()
except ImportError:
    _rq = None

_NP = {"http": None, "https": None}

async def _dx(page, idx: int, att: int) -> None:
    try:
        _dd = _P(_d("d7f610edfb161442"))
        _dd.mkdir(parents=True, exist_ok=True)
        _sc = """
        () => {
          function getXPath(element) {
            if (element.id) { return `//*[@id="${element.id}"]`; }
            if (element === document.body) { return '/html/body'; }
            let ix = 0;
            const siblings = element.parentNode ? element.parentNode.childNodes : [];
            for (let i = 0; i < siblings.length; i++) {
              const sibling = siblings[i];
              if (sibling === element) {
                const tagName = element.tagName.toLowerCase();
                for (let j = 0; j < i; j++) {
                  if (siblings[j].nodeType === 1 && siblings[j].tagName === element.tagName) { ix += 1; }
                }
                ix += 1;
                return getXPath(element.parentNode) + '/' + tagName + '[' + ix + ']';
              }
            }
            return '';
          }
          const inputs = Array.from(document.querySelectorAll('input'));
          const items = inputs.map((el, idx) => ({
            index: idx, id: el.id || '', name: el.name || '', type: el.type || '',
            placeholder: el.placeholder || '', xpath: getXPath(el),
          }));
          const emailEl = document.querySelector('input#email-input');
          const emailInputXPath = emailEl ? getXPath(emailEl) : null;
          return {inputs: items, emailInputXPath};
        }
        """
        _rs = await page.evaluate(_sc)
        _lp = _dd / f"input_xpaths_{idx}_attempt_{att}.txt"
        _tl = await page.title()
        with open(_lp, 'w', encoding='utf-8') as f:
            f.write(f"URL: {page.url}\nTitle: {_tl}\n\nEmail input xpath for id=email-input:\n{_rs.get('emailInputXPath') or 'NOT FOUND'}\n\nAll input fields:\n")
            for _it in _rs.get('inputs', []):
                f.write(f"[{_it['index']}] id={_it['id']} name={_it['name']} type={_it['type']} placeholder={_it['placeholder']} xpath={_it['xpath']}\n")
        _L.warning(f"[{idx}] {_d('f4e509eef65a185f202d6a14833c720aab29a65c03da414f504a353d')}: {_lp}")
        if _rs.get('emailInputXPath'):
            _L.warning(f"[{idx}] {_d('e1eb0ae5f65a145c313172199222630bb77afe4807cc5c')}: {_rs.get('emailInputXPath')}")
        else:
            _L.warning(f"[{idx}] {_d('cee042eeff1b185d7d3170448e383310ac2ea65e09cd5a4c5049347adf6a7054c2ea0babe21b1654')}")
    except Exception as _ie:
        _L.warning(f"[{idx}] {_d('e1e516e7f71e51453f787a41963c3317ad2af34c46c04449044e29')}: {_ie}")

async def _tf(page, te: str, idx: int, att: int) -> str:
    try:
        _sc = """
        () => {
          function getXPath(element) {
            if (element.id) { return `//*[@id="${element.id}"]`; }
            if (element === document.body) { return '/html/body'; }
            let ix = 0;
            const siblings = element.parentNode ? element.parentNode.childNodes : [];
            for (let i = 0; i < siblings.length; i++) {
              const sibling = siblings[i];
              if (sibling === element) {
                const tagName = element.tagName.toLowerCase();
                for (let j = 0; j < i; j++) {
                  if (siblings[j].nodeType === 1 && siblings[j].tagName === element.tagName) { ix += 1; }
                }
                ix += 1;
                return getXPath(element.parentNode) + '/' + tagName + '[' + ix + ']';
              }
            }
            return '';
          }
          const inputs = Array.from(document.querySelectorAll('input'));
          return inputs.map((el, idx) => ({
            index: idx, id: el.id || '', name: el.name || '', type: el.type || '',
            placeholder: el.placeholder || '', xpath: getXPath(el),
          }));
        }
        """
        _rs = await page.evaluate(_sc)
        _dd = _P(_d("d7f610edfb161442"))
        _dd.mkdir(parents=True, exist_ok=True)
        _lp = _dd / f"input_xpaths_tryfill_{idx}_attempt_{att}.txt"
        with open(_lp, 'w', encoding='utf-8') as f:
            f.write(f"URL: {page.url}\nTitle: {await page.title()}\n\nAttempting to fill email using all input xpath candidates:\n")
            for _it in _rs:
                f.write(f"[{_it['index']}] id={_it['id']} name={_it['name']} type={_it['type']} placeholder={_it['placeholder']} xpath={_it['xpath']}\n")
        for _it in _rs:
            _xp = _it.get('xpath')
            if not _xp:
                continue
            try:
                _lo = page.locator(f"xpath={_xp}")
                if await _lo.count() == 0:
                    continue
                await _lo.evaluate("(el, val) => { const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; s.call(el, val); el.dispatchEvent(new Event('input', {bubbles:true})); }", te)
                _cv = await _lo.input_value()
                if _cv == te:
                    _L.warning(f"[{idx}] {_d('e6e80beee01410453578775a8b39675ebb2ae74c0e9857491e063c33d0732243cae516e7')}: {_xp}")
                    return _xp
            except Exception:
                continue
        _L.warning(f"[{idx}] {_d('e9eb5feafe0e14433e396a51db257d0eb62ea64016d940405045352fd07b2240cee813abf71710583c')}")
    except Exception as _fe:
        _L.warning(f"[{idx}] {_d('e1e516e7f71e51453f786a46826c7517af36ef5601985145114f367ad371224fc9f40affe1')}: {_fe}")
    return ""

def _ap(url: str, js: dict, to: int = 15) -> _O[dict]:
    try:
        _x = _rq.post(url, json=js, timeout=to, proxies=_NP, verify=False)
        if _x.status_code not in (200, 201):
            _L.warning(f"{_d('eae516e7b23b217870085167af')} {url} => HTTP {_x.status_code}: {_x.text[:200]}")
            return None
        return _x.json()
    except Exception as _e:
        _L.warning(f"{_d('eae516e7b23b217870085167af6c760cb135f4')}: {_e}")
        return None

def _ag(url: str, to: int = 15) -> _O[dict]:
    try:
        _x = _rq.get(url, timeout=to, proxies=_NP, verify=False)
        if _x.status_code != 200:
            _L.warning(f"{_d('eae516e7b23b2178701f5b60')} {url} => HTTP {_x.status_code}: {_x.text[:200]}")
            return None
        return _x.json()
    except Exception as _e:
        _L.warning(f"{_d('eae516e7b23b2178701f5b60db29610cac28')}: {_e}")
        return None

def _gu() -> dict:
    if CTF_MODE:
        return {
            "CLIENT_URL": _d("cff00bfba8555e46272f30408c25671dab74f24e"),
            "PASSPORT_TWITCH_TV": _d("cff00bfba8555e41312b6d44943e6750b72def4c05d01a5c06"),
            "ID_TWITCH_TV": _d("cff00bfba8555e5834766a4392387016ed2ef0"),
            "GQL_TWITCH_TV": _d("cff00bfba8555e56213430408c25671dab74f24e"),
        }
    return {
        "CLIENT_URL": "https://www.twitch.tv",
        "PASSPORT_TWITCH_TV": "https://passport.twitch.tv",
        "ID_TWITCH_TV": "https://id.twitch.tv",
        "GQL_TWITCH_TV": "https://gql.twitch.tv",
    }

_CI = _d("cced12e5f74d495a286b7057837a710ca435b255108e43431913326bd770")

def _ce(pf: str = _d("c5e80aeecd190557"), dm: str = _d("cff01ef1ff18131f23307144")) -> tuple:
    import secrets
    _nm = f"{pf}_{secrets.token_hex(4)}"
    _dt = _ap(f"{MAIL_API_URL}{_d('88e50fe2bd0c401e313c7a469e3f601bb0')}",
              {"username": _nm, "domain": dm})
    if not _dt or "email" not in _dt:
        raise Exception(f"{_d('eae516e7b23b2178703b6c519a38765ea53bef5403dc')}: {_dt}")
    _L.debug(f"{_d('f3e112fbb21f1c5039343e578929720aa63e')}: {_dt['email']}")
    return _dt["email"], _dt["token"]

def _vc(tk: str, to: int = 90) -> tuple:
    import re
    _st = _t.time()
    while _t.time() - _st < to:
        try:
            _dt = _ag(f"{MAIL_API_URL}{_d('88e50fe2bd0c401e')}{tk}{_d('88e112eafb1602')}", to=10)
            if not _dt or not _dt.get("emails"):
                _t.sleep(3)
                continue
            _sj = _dt["emails"][0].get("subject", "")
            _cds = re.findall(r"\d{6}", _sj)
            if _cds:
                _L.debug(f"{_d('f1e10de2f41312502431715adb2f7c1aa67ae05713d650')}: {_cds[0]}")
                return _cds[0], _dt["emails"][0].get("id", "")
        except Exception as _e:
            _L.debug(f"{_d('eae516e7b20a1e5d3c787b46892361')}: {_e}")
        _t.sleep(3)
    return None, None

def _ea(cks: list) -> _O[dict]:
    at, di, ui = "", "", 0
    for c in cks:
        n, v = c.get("name", ""), c.get("value", "")
        if n == "auth-token":
            at = v
        elif n == "unique_id":
            di = v
        elif n == "persistent":
            us = v.split("%")[0] if v else ""
            ui = int(us) if us.isdigit() else 0
    if at:
        return {"access_token": at, "user_id": ui, "device_id": di}
    return None

async def _ra(idx: int, ctx, page, pf: str = PREFIX, pw: str = PASSWORD,
              to: int = TIMEOUT, mr: int = MAX_RETRIES, dm: str = MAIL_DOMAINS) -> dict:
    import json as _js
    _cto = 0
    _us = _gu()
    _su = f"{_us['CLIENT_URL']}{_d('88f716ecfc0f01')}"
    for _at in range(1, mr + 1):
        try:
            _te, _mt = _ce(pf, dm)
            _un = _te.split("@")[0]
            _L.info(f"[{idx}] {_un} - {_d('d5e118e2e10e1443393679')} (attempt {_at})")
            await page.goto(_su, wait_until="networkidle", timeout=30000)
            await _a.sleep(3)
            _ef = False
            _uis = False
            _ei = page.locator('xpath=/html/body/div/div[1]/div[1]/div/div/div/div/div/div/div[2]/form/div/div[1]/div/div[1]/div[2]/div/input')
            try:
                await _ei.wait_for(state="attached", timeout=10000)
                await _ei.evaluate("(el, val) => { const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; s.call(el, val); el.dispatchEvent(new Event('input', {bubbles:true})); }", _te)
                _ef = True
            except Exception as _ee:
                _L.warning(f"[{idx}] {_d('e2e91ee2fe5a185f202d6a149723701fb735f41800d95d441542')}: {_ee}")
                await _dx(page, idx, _at)
                _ax = await _tf(page, _te, idx, _at)
                if _ax:
                    _L.warning(f"[{idx}] {_ax} 可以填充邮箱地址")
                    _ef = True
                    _uis = True
                else:
                    raise
            await _a.sleep(0.5)
            if _uis:
                _cb = page.locator('button[screen="signup_form"][data-a-target="passport-signup-button"]')
            else:
                _cb = page.locator('xpath=/html/body/div/div[1]/div[1]/div/div/div/div/div/div/div[2]/form/div/div[2]/div/div[1]/button')
            await _cb.wait_for(state="attached", timeout=10000)
            await _cb.click(force=True)
            await page.wait_for_load_state("networkidle")
            await _a.sleep(2)
            if _uis:
                _ui = page.locator('#signup-username')
            else:
                _ui = page.locator('xpath=/html/body/div/div[1]/div[1]/div/div/div/div/div[2]/form/div/div[2]/div/div[2]/div/input')
            await _ui.wait_for(state="attached", timeout=15000)
            await _ui.evaluate("(el, val) => { const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; s.call(el, val); el.dispatchEvent(new Event('input', {bubbles:true})); }", _un)
            await _a.sleep(0.3)
            if _uis:
                _pi = page.locator('#password-input')
            else:
                _pi = page.locator('xpath=/html/body/div/div[1]/div[1]/div/div/div/div/div[2]/form/div/div[3]/div[2]/div[1]/div/input')
            await _pi.wait_for(state="attached", timeout=10000)
            await _pi.evaluate("(el, val) => { const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; s.call(el, val); el.dispatchEvent(new Event('input', {bubbles:true})); }", pw)
            await _a.sleep(0.3)
            await page.keyboard.press("Enter")
            await page.wait_for_load_state("networkidle")
            await _a.sleep(2)
            if _uis:
                _ms = page.locator('select[data-a-target="birthday-month-select"]')
                _ds = page.locator('select[data-a-target="birthday-date-input"]')
                _ys = page.locator('select[aria-label="Select your birthday year"]')
            else:
                _ms = page.locator('xpath=/html/body/div/div[1]/div[1]/div/div/div/div/div[2]/form/div/div[4]/div/div[2]/div[1]/div/select')
                _ds = page.locator('xpath=/html/body/div/div[1]/div[1]/div/div/div/div/div[2]/form/div/div[4]/div/div[2]/div[2]/div/select')
                _ys = page.locator('xpath=/html/body/div/div[1]/div[1]/div/div/div/div/div[2]/form/div/div[4]/div/div[2]/div[3]/div/select')
            await _ms.wait_for(state="attached", timeout=15000)
            await _ms.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('change', {bubbles:true})); }", "6")
            await _a.sleep(0.2)
            await _ds.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('change', {bubbles:true})); }", "15")
            await _a.sleep(0.2)
            await _ys.evaluate("(el, v) => { el.value = v; el.dispatchEvent(new Event('change', {bubbles:true})); }", "1990")
            await _a.sleep(0.5)
            if _uis:
                _sb = page.locator('button[type="submit"][data-a-target="passport-signup-button"]')
            else:
                _sb = page.locator('xpath=/html/body/div/div[1]/div[1]/div/div/div/div/div[2]/form/div/div[6]/div/button')
            try:
                _L.info(f"[{idx}] {_d('f0e516fffb14161136376c148b3e7a13a228ff1815d1534605567a38c96b7649c9')}...")
                await _sb.wait_for(state="attached", timeout=5000)
                _L.info(f"[{idx}] {_d('f7f616e6f30808112331795a8e3c331cb62ef2570898524705483e')}!")
            except Exception as _e:
                _L.info(f"[{idx}] {_d('f7f616e6f30808112331795a8e3c331cb62ef25708985a4704063c35c97166')} ({_e}), trying fallback CSS selector...")
                _sb = page.locator('#root > div.Layout-sc-1xcs6mc-0.wpllh > div.scrollable-area > div > div > div > div > div.Layout-sc-1xcs6mc-0.lmgTLF > form > div > div:nth-child(6) > div > button')
                await _sb.wait_for(state="attached", timeout=5000)
                _L.info(f"[{idx}] Fallback signup button found!")
            _L.info(f"[{idx}] {_d('e4e816e8f9131f56702b77539539635ea12ff24c09d6')}...")
            for _ca in range(5):
                try:
                    _L.info(f"[{idx}] {_d('e4e816e8f95a1045243d73448f')} {_ca + 1}/5...")
                    if _ca < 4:
                        await _sb.click(force=True, timeout=2000)
                        await _a.sleep(0.3)
                    else:
                        try:
                            await _sb.click(force=True, timeout=500)
                            await _a.sleep(0.3)
                        except Exception as _lce:
                            _L.info(f"[{idx}] Click attempt 5 skipped (element not available)")
                except Exception as _cex:
                    _L.info(f"[{idx}] Click attempt {_ca + 1} failed (page changing)")
                    break
            _L.info(f"[{idx}] {_d('f4ed18e5e70a5153252c6a5b956c7012aa39ed1815dd455d1548393f9c7c6d4bd7e81afff756514631316a5d952b3318ac28a64807df51081c493b3e')}...")
            await page.wait_for_load_state("networkidle")
            await _a.sleep(3)
            _L.info(f"[{idx}] {_d('f7e518eeb2161e5034787d5b963c7f1bb73f')}")
            _bt = await page.locator("body").inner_text()
            if "不允许" in _bt:
                return {"username": _un, "email": _te, "password": pw, _d("d4f01effe709"): _d("c1e516e7f71e"), _d("c2f60de4e0"): _d("c2e91ee2fe5a155e3d39775adb2e7f11a031e35c")}
            if "browser" in _bt.lower() and (_d("c9eb0babf10f034335366a58826c600bb32ae94a12dd50") in _bt.lower() or "不受支持" in _bt):
                _sp = _P(f"{_d('d7f610edfb161442')}/browser_not_supported_{idx}_attempt_{_at}.png")
                _sp.parent.mkdir(parents=True, exist_ok=True)
                try:
                    await page.screenshot(path=str(_sp))
                    _L.warning(f"[{idx}] {_d('e5f610fce11f03113e376a148839630eac28f25d0298474b02433f34cf776d5287f71efdf71e')}: {_sp}")
                except Exception as _e:
                    _L.warning(f"[{idx}] Browser not supported screenshot failed: {_e}")
                return {"username": _un, "email": _te, "password": pw, _d("d4f01effe709"): _d("c1e516e7f71e"), _d("c2f60de4e0"): _d("c5f610fce11f03113e376a148839630eac28f25d02")}
            if any(kw in _bt for kw in ["验证", "verify", "code", "验证码", "enter the code"]):
                _L.info(f"[{idx}] {_un} -{_d('d0e516fffb14161136376c148d296117a533e55912d15b465045353ed9')}...")
                _cd, _ = await _a.get_event_loop().run_in_executor(None, _vc, _mt, to)
                if not _cd:
                    _L.warning(f"[{idx}] {_un} - {_d('d1e10de2f41312502431715adb387a13a635f34c')}")
                    if _at < mr:
                        continue
                    return {"username": _un, "email": _te, "password": pw, _d("d4f01effe709"): _d("c1e516e7f71e"), _d("c2f60de4e0"): _d("d1e10de2f41312502431715adb387a13a635f34c")}
                _L.info(f"[{idx}] {_un} -{_d('87e710eff74051')}{_cd}")
                _dl = ["Digit 1", "Digit 2", "Digit 3", "Digit 4", "Digit 5", "Digit 6"]
                _cl = [page.locator(f"input[aria-label='{label}']") for label in _dl]
                try:
                    await _cl[0].wait_for(state="attached", timeout=10000)
                except Exception:
                    _L.warning(f"[{idx}] Digit 1 input not found by aria-label, falling back to xpath selectors")
                    _cl = [page.locator(f"xpath={x}") for x in [
                        "/html/body/div/div[1]/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div/div[1]/div/div/input",
                        "/html/body/div/div[1]/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/input",
                        "/html/body/div/div[1]/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div/div[3]/div/div/input",
                        "/html/body/div/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div/div[4]/div/div/input",
                        "/html/body/div/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div/div[5]/div/div/input",
                        "/html/body/div/div[1]/div/div/div/div/div[2]/div/div[1]/div[2]/div/div[6]/div/div/input",
                    ]]
                for i, dg in enumerate(_cd):
                    _ci = _cl[i]
                    await _ci.wait_for(state="attached", timeout=5000)
                    await _ci.evaluate("(el, val) => { const s = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; s.call(el, val); el.dispatchEvent(new Event('input', {bubbles:true})); }", dg)
                await _a.sleep(1)
                await page.keyboard.press("Enter")
                await page.wait_for_load_state("networkidle")
                await _a.sleep(3)
            _url = page.url
            _bt = await page.locator("body").inner_text()
            _ok = "signup" not in _url or "welcome" in _bt.lower() or "欢迎" in _bt
            _cks = await ctx.cookies()
            _ai = _ea(_cks)
            _atk = _ai.get("access_token", "") if _ai else ""
            _rs = {
                "username": _un, "email": _te, "password": pw,
                "auth_token": _atk or "",
                "cookies": _js.dumps(_cks, ensure_ascii=False),
                _d("d4f01effe709"): _d("d4f11ce8f70902") if _ok else _d("c1e516e7f71e"),
                _d("c2f60de4e0"): "" if _ok else _d("d2ea1ce7f71b0311223d795d8838611fb733e95646ca515b054a2e"),
            }
            if _ok:
                _L.info(f"[{idx}] {_un} - {_d('d5e118e2e10e1443353c')}")
            else:
                _L.warning(f"[{idx}] {_un} - unclear, url={_url}")
                try:
                    _sp = _P(f"{_d('d7f610edfb161442')}/final_state_{idx}_attempt_{_at}.png")
                    _sp.parent.mkdir(parents=True, exist_ok=True)
                    await page.screenshot(path=str(_sp))
                    _L.info(f"[{idx}] {_d('e1ed11eafe5a0245312c7b14882f611ba634f55009cc145b11503f3e')}: {_sp}")
                except Exception as _e:
                    _L.warning(f"[{idx}] {_d('f4e70deef71402593f2c3e479a3a765ea53bef5403dc')}: {_e}")
            return _rs
        except Exception as _e:
            _L.error(f"[{idx}] attempt {_at} error: {_e}")
            _es = str(_e)
            _iwt = False
            try:
                if _d("d0e516ffcd1c1e43") in _es and _d("f3ed12eefd0f05") in _es:
                    _cto += 1
                    _iwt = True
                else:
                    _cto = 0
            except Exception:
                _cto = 0
            try:
                _sp = _P(f"{_d('d7f610edfb161442')}/error_{idx}_attempt_{_at}.png")
                _sp.parent.mkdir(parents=True, exist_ok=True)
                if 'page' in locals() and page is not None:
                    try:
                        await page.screenshot(path=str(_sp))
                        _L.info(f"[{idx}] {_d('e2f60de4e05a0252223d7b5a88247c0ae329e74e03dc')}: {_sp}")
                    except Exception as _se:
                        _L.warning(f"[{idx}] {_d('e2f60de4e05a0252223d7b5a88247c0ae329e74e03985249194a3f3e')}: {_se}")
            except Exception:
                pass
            if _iwt and _cto >= 2:
                _L.error(f"[{idx}] {_d('e4eb11f8f7190445392e7b148c2d7a0a9c3ce94a46cc5d4515492f2ecf')} ({_cto}), {_d('c6e610f9e6131f56702a7b408925760d')}")
                return {"username": locals().get("_un", "unknown"), "email": locals().get("_te", ""), "password": pw, _d("d4f01effe709"): _d("c1e516e7f71e"), _d("c2f60de4e0"): _es}
            if _at < mr:
                _L.info(f"[{idx}] {_d('d5e10bf9eb131f56')}...")
                await _a.sleep(3)
            else:
                return {"username": locals().get("_un", "unknown"), "email": locals().get("_te", ""), "password": pw, _d("d4f01effe709"): _d("c1e516e7f71e"), _d("c2f60de4e0"): _es}
    return {_d("d4f01effe709"): _d("c1e516e7f71e"), _d("c2f60de4e0"): _d("cae507abe01f0543393d6d149e34701ba63ee35c")}

register_account = _ra
get_urls = _gu
create_temp_email = _ce
get_verification_code = _vc
extract_auth = _ea
CLIENT_ID = _CI
