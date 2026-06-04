# main.py - Registration client entry point
# reg/main.py

import asyncio
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from loguru import logger

from .config import (
    THREADS, REGISTER_COUNT, PREFIX, PASSWORD, TIMEOUT, MAX_RETRIES,
    PROXY_FILE, CLASH_API, CLASH_GROUP, CLASH_SECRET, NO_HEADLESS, CTF_MODE,
)
from .api_client import APIClient
from .twitch_registration import register_account

logger.remove()
_log_level = os.environ.get("LOGURU_LEVEL", os.environ.get("DEBUG", "false").lower() == "true" and "DEBUG" or "INFO")
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level=_log_level,
)
logger.add(
    Path(__file__).parent / "reg_linux_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
)

os.environ["TWITCH_CTF"] = "1" if CTF_MODE else "0"


def load_proxies(path: str) -> list:
    if not path or not Path(path).exists():
        return []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]


async def run_registration(
    index: int,
    api_client: APIClient,
) -> None:
    try:
        from cloakbrowser import launch_persistent_context_async
        logger.debug(f"[{index}] cloakbrowser imported OK")
    except ImportError:
        logger.error("cloakbrowser not installed. Run: pip install cloakbrowser playwright")
        return

    session_dir = Path("./profiles") / f"reg_profile_{index}"
    session_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"[{index}] session_dir={session_dir}")

    launch_kwargs = {
        "user_data_dir": str(session_dir),
        "headless": True,
        "args": [f"--fingerprint={10000 + index}"],
        "locale": "zh-CN",
    }

    logger.info(f"[{index}] Launching browser")
    try:
        context = await asyncio.wait_for(
            launch_persistent_context_async(**launch_kwargs),
            timeout=60
        )
        logger.debug(f"[{index}] Browser launched OK")

        if not context.pages:
            page = await context.new_page()
        else:
            page = context.pages[0]
        logger.debug(f"[{index}] Page ready, starting registration")

        result = await register_account(
            index=index,
            context=context,
            page=page,
            prefix=PREFIX,
            password=PASSWORD,
            timeout=TIMEOUT,
            max_retries=MAX_RETRIES,
        )

        if result.get("status") == "success":
            uploaded = api_client.upload_account(
                username=result["username"],
                password=result["password"],
                email=result.get("email", ""),
                auth_token=result.get("auth_token", ""),
                cookies=result.get("cookies", ""),
            )
            if uploaded:
                logger.info(f"[{index}] {result['username']} - uploaded to API")
            else:
                logger.warning(f"[{index}] {result['username']} - API upload failed")
        else:
            logger.warning(f"[{index}] Registration failed: {result.get('error')}")

        await context.close()
        # Clean up profile after successful upload
        if result.get("status") == "success" and result.get("cookies"):
            import shutil
            try:
                shutil.rmtree(str(session_dir), ignore_errors=True)
                logger.debug(f"[{index}] Profile cleaned: {session_dir}")
            except Exception:
                pass
    except asyncio.TimeoutError:
        logger.error(f"[{index}] Browser launch timeout (60s)")
    except Exception as e:
        logger.error(f"[{index}] Browser error: {e}")


async def main() -> None:
    api_client = APIClient()

    logger.info(f"Starting registration: {REGISTER_COUNT} accounts, {THREADS} threads")

    sem = asyncio.Semaphore(THREADS)
    completed = 0
    lock = asyncio.Lock()

    async def run_one(i: int) -> None:
        nonlocal completed
        async with sem:
            api_client.heartbeat("reg_worker", "reg")
            await run_registration(i, api_client)
            async with lock:
                completed += 1
                logger.info(f"Progress: {completed}/{REGISTER_COUNT}")

    tasks = [asyncio.create_task(run_one(i)) for i in range(REGISTER_COUNT)]
    await asyncio.gather(*tasks)

    api_client.heartbeat("reg_worker", "reg")
    logger.info(f"Registration complete. {REGISTER_COUNT} accounts attempted.")


def entry():
    asyncio.run(main())


if __name__ == "__main__":
    entry()
