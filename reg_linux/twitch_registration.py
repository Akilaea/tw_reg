# twitch_registration.py - Adapted from cloakminer.registration
# reg/twitch_registration.py

import asyncio
import os
import time
from pathlib import Path
from typing import Optional

from loguru import logger

from .config import PREFIX, PASSWORD, TIMEOUT, MAX_RETRIES, CTF_MODE, MAIL_API_URL, MAIL_ADMIN_AUTH, MAIL_DOMAINS

try:
    import requests as sync_requests
    from urllib3 import disable_warnings as _dw
    _dw()
except ImportError:
    sync_requests = None


def _get_proxies() -> dict:
    p = {}
    for key in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
        val = os.environ.get(key, "")
        if val:
            p["https"] = val
            p["http"] = val
            break
    return p


def _api_get(url: str, timeout: int = 15) -> Optional[dict]:
    try:
        resp = sync_requests.get(url, timeout=timeout, proxies=_get_proxies())
        if resp.status_code != 200:
            logger.warning(f"Mail API GET {url} => HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        return resp.json()
    except Exception as e:
        logger.warning(f"Mail API GET error: {e}")
        return None


def _api_post(url: str, json_data: dict, timeout: int = 15) -> Optional[dict]:
    try:
        resp = sync_requests.post(url, json=json_data, timeout=timeout, proxies=_get_proxies())
        if resp.status_code not in (200, 201):
            logger.warning(f"Mail API POST {url} => HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        return resp.json()
    except Exception as e:
        logger.warning(f"Mail API POST error: {e}")
        return None


__no_proxy = {"http": None, "https": None}


def _api_post_admin(url: str, json_data: dict, timeout: int = 15) -> Optional[dict]:
    try:
        resp = sync_requests.post(
            url,
            json=json_data,
            timeout=timeout,
            proxies=__no_proxy,
            headers={"x-admin-auth": MAIL_ADMIN_AUTH},
            verify=False,
        )
        if resp.status_code not in (200, 201):
            logger.warning(f"Mail Admin API POST {url} => HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        return resp.json()
    except Exception as e:
        logger.warning(f"Mail Admin API POST error: {e}")
        return None


def _api_get_jwt(url: str, jwt: str, timeout: int = 15) -> Optional[dict]:
    try:
        resp = sync_requests.get(
            url,
            timeout=timeout,
            proxies=__no_proxy,
            headers={"Authorization": f"Bearer {jwt}"},
            verify=False,
        )
        if resp.status_code != 200:
            logger.warning(f"Mail JWT API GET {url} => HTTP {resp.status_code}: {resp.text[:200]}")
            return None
        return resp.json()
    except Exception as e:
        logger.warning(f"Mail JWT API GET error: {e}")
        return None


def get_urls() -> dict:
    if CTF_MODE:
        return {
            "CLIENT_URL": "http://www.twitch.tv",
            "PASSPORT_TWITCH_TV": "http://passport.twitch.tv",
            "ID_TWITCH_TV": "http://id.twitch.tv",
            "GQL_TWITCH_TV": "http://gql.twitch.tv",
        }
    return {
        "CLIENT_URL": "https://www.twitch.tv",
        "PASSPORT_TWITCH_TV": "https://passport.twitch.tv",
        "ID_TWITCH_TV": "https://id.twitch.tv",
        "GQL_TWITCH_TV": "https://gql.twitch.tv",
    }


CLIENT_ID = "kimne78kx3ncx6brgo4mv6wki5h1ko"


def create_temp_email(prefix: str = "blue_ctf") -> tuple:
    import secrets, random
    name = f"{prefix}_{secrets.token_hex(4)}"
    domains = [d.strip() for d in MAIL_DOMAINS.split(",") if d.strip()]
    if not domains:
        domains = ["xiiktcx.cn", "cabuhu.cn"]
    domain = random.choice(domains)
    data = _api_post_admin(
        f"{MAIL_API_URL}/admin/new_address",
        {"enablePrefix": True, "name": name, "domain": domain},
    )
    if not data or "address" not in data:
        raise Exception(f"Mail API create failed: {data}")
    logger.debug(f"Temp email created: {data['address']}")
    return data["address"], data["jwt"]


def get_verification_code(jwt: str, timeout: int = 90) -> tuple:
    import re
    start = time.time()
    while time.time() - start < timeout:
        try:
            data = _api_get_jwt(f"{MAIL_API_URL}/api/mails?limit=1&offset=0", jwt, timeout=10)
            if not data or not data.get("results"):
                time.sleep(3)
                continue
            raw = data["results"][0].get("raw", "")
            codes = re.findall(r"(?<=>)\d{6}(?=<)", raw)
            if codes:
                logger.debug(f"Verification code found: {codes[0]}")
                return codes[0], data["results"][0].get("id", "")
        except Exception as e:
            logger.debug(f"Mail poll error: {e}")
        time.sleep(3)
    return None, None


def extract_auth(cookies: list) -> Optional[dict]:
    auth_token = ""
    device_id = ""
    user_id = 0
    for c in cookies:
        name = c.get("name", "")
        value = c.get("value", "")
        if name == "auth-token":
            auth_token = value
        elif name == "unique_id":
            device_id = value
        elif name == "persistent":
            user_id_str = value.split("%")[0] if value else ""
            user_id = int(user_id_str) if user_id_str.isdigit() else 0
    if auth_token:
        return {"access_token": auth_token, "user_id": user_id, "device_id": device_id}
    return None


async def register_account(
    index: int,
    context,
    page,
    prefix: str = PREFIX,
    password: str = PASSWORD,
    timeout: int = TIMEOUT,
    max_retries: int = MAX_RETRIES,
) -> dict:
    """Register a single Twitch account using CloakBrowser/Playwright."""
    import json as _json

    urls = get_urls()
    signup_url = f"{urls['CLIENT_URL']}/signup"

    for attempt in range(1, max_retries + 1):
        try:
            temp_email, mail_token = create_temp_email(prefix)
            username = temp_email.split("@")[0]
            logger.info(f"[{index}] {username} - registering (attempt {attempt})")

            await page.goto(signup_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            # Diagnostic: log what the browser actually sees
            actual_url = page.url
            actual_title = await page.title()
            body_text = await page.locator("body").inner_text()
            logger.debug(f"[{index}] URL: {actual_url}")
            logger.debug(f"[{index}] Title: {actual_title}")
            logger.debug(f"[{index}] Body preview: {body_text[:500]}")

            # Take screenshot for debugging
            screenshot_path = Path(f"profiles/debug_{index}_attempt_{attempt}.png")
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path))
            logger.debug(f"[{index}] Screenshot saved: {screenshot_path}")

            email_input = page.locator('input#email-input, input[type="email"]').first
            await email_input.click()
            await email_input.fill(temp_email)
            await page.wait_for_timeout(500)

            signup_btn = page.locator('[data-a-target="passport-signup-button"]').first
            await signup_btn.click()
            await page.wait_for_timeout(3000)

            text_inputs = page.locator('input[type="text"]')
            count = await text_inputs.count()
            for i in range(count):
                inp = text_inputs.nth(i)
                if await inp.is_visible():
                    await inp.click()
                    await inp.fill(username)
                    break

            password_input = page.locator('input[type="password"]').first
            await password_input.click()
            await password_input.fill(password)
            await page.wait_for_timeout(500)

            signup_btn = page.locator('[data-a-target="passport-signup-button"]').first
            await signup_btn.click()
            await page.wait_for_timeout(3000)

            selects = page.locator("select")
            select_count = await selects.count()
            visible_selects = []
            for i in range(select_count):
                s = selects.nth(i)
                if await s.is_visible():
                    visible_selects.append(s)
            if len(visible_selects) >= 1:
                await visible_selects[0].select_option("1990")
            if len(visible_selects) >= 2:
                await visible_selects[1].select_option("6")
            if len(visible_selects) >= 3:
                await visible_selects[2].select_option("15")
            await page.wait_for_timeout(500)

            signup_btn = page.locator('[data-a-target="passport-signup-button"]').first
            await signup_btn.click()
            await page.wait_for_timeout(8000)

            body_text = await page.locator("body").inner_text()

            if "不允许" in body_text:
                return {"username": username, "email": temp_email, "password": password, "status": "failed", "error": "email domain blocked"}

            if "browser" in body_text.lower() and ("not currently supported" in body_text.lower() or "不受支持" in body_text):
                return {"username": username, "email": temp_email, "password": password, "status": "failed", "error": "browser not supported"}

            if any(kw in body_text for kw in ["验证", "verify", "code", "验证码", "enter the code"]):
                logger.info(f"[{index}] {username} - waiting for verification code...")
                code, _ = await asyncio.get_event_loop().run_in_executor(
                    None, get_verification_code, mail_token, timeout
                )
                if not code:
                    logger.warning(f"[{index}] {username} - verification timeout")
                    if attempt < max_retries:
                        continue
                    return {"username": username, "email": temp_email, "password": password, "status": "failed", "error": "verification timeout"}

                logger.info(f"[{index}] {username} - code: {code}")

                code_inputs = page.locator('input[type="text"], input[type="number"], input[inputmode="numeric"]')
                ci_count = await code_inputs.count()
                visible_ci = []
                for i in range(ci_count):
                    ci = code_inputs.nth(i)
                    if await ci.is_visible():
                        visible_ci.append(ci)
                if len(visible_ci) == 6:
                    for i, digit in enumerate(code):
                        await visible_ci[i].fill(digit)
                        await page.wait_for_timeout(100)
                elif visible_ci:
                    await visible_ci[0].fill(code)
                await page.wait_for_timeout(1000)

                submitted = False
                try:
                    submit_btn = page.locator('button[data-a-target*="submit"]').first
                    if await submit_btn.is_visible():
                        await submit_btn.click()
                        submitted = True
                except Exception:
                    pass
                if not submitted:
                    await page.keyboard.press("Enter")
                await page.wait_for_timeout(10000)

            url = page.url
            body_text = await page.locator("body").inner_text()
            success = "signup" not in url or "welcome" in body_text.lower() or "欢迎" in body_text

            cookies = await context.cookies()
            auth_info = extract_auth(cookies)
            auth_token = auth_info.get("access_token", "") if auth_info else ""

            result = {
                "username": username,
                "email": temp_email,
                "password": password,
                "auth_token": auth_token or "",
                "cookies": _json.dumps(cookies, ensure_ascii=False),
                "status": "success" if success else "failed",
                "error": "" if success else "unclear registration result",
            }

            if success:
                logger.info(f"[{index}] {username} - registered")
            else:
                logger.warning(f"[{index}] {username} - unclear, url={url}")

            return result

        except Exception as e:
            logger.error(f"[{index}] attempt {attempt} error: {e}")
            if attempt < max_retries:
                logger.info(f"[{index}] retrying...")
                await page.wait_for_timeout(3000)
            else:
                return {"username": locals().get("username", "unknown"), "email": locals().get("temp_email", ""), "password": password, "status": "failed", "error": str(e)}

    return {"status": "failed", "error": "max retries exceeded"}
