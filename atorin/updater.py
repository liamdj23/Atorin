import hashlib
import sys
import os
import subprocess
import yaml
import httpx

from quart import Request
from .logger import log
from .config import config
import hmac


def restart_process() -> None:
    python = sys.executable
    os.execl(python, python, *sys.argv)


def send_webhook(message: str) -> None:
    data = {}
    data["embeds"] = [{"description": message, "color": 16711680}]
    r = httpx.post(config["updater"]["webhook"], json=data)
    try:
        r.raise_for_status()
    except httpx.exceptions.HTTPError as err:
        log.error(f"Updater :: Webhook :: {err}")


def check_config_for_changes() -> set:
    with open("config.yml.example", "r") as file:
        example = yaml.safe_load(file)
        diff = set(config) - set(example)
        return diff


def update_dependencies() -> bool:
    pip = sys.executable.replace("python", "pip")
    try:
        subprocess.check_call(f"{pip} install -r requirements.txt".split())
    except subprocess.CalledProcessError:
        return False
    return True


def pull_update() -> bool:
    try:
        subprocess.check_call("git pull".split())
    except subprocess.CalledProcessError:
        return False
    return True


async def check_signature(request: Request) -> bool:
    signature = request.headers["X-Hub-Signature"]
    if not signature.startswith("sha1="):
        return False
    data = await request.data
    digest = hmac.new(
        config["updater"]["webhook"].encode(), data, hashlib.sha1
    ).hexdigest()
    if not hmac.compare_digest(signature, f"sha1={digest}"):
        return False
    return True


def process_update() -> None:
    log.info("⬇️ Downloading update...")
    if not pull_update():
        log.error("❌ Downloading updates has failed!")
        send_webhook("⬇️ Nie udało się pobrać aktualizacji.")
        return
    log.info("✅ Update downloaded successfully!")
    log.info("📦 Updating dependencies...")
    if not update_dependencies():
        log.error("❌ Updating dependencies has failed!")
        send_webhook("📦 Nie udało się uaktualnić zależności.")
        return
    log.info("✅ Dependencies updated successfully!")
    log.info("📝 Checking config for new entries...")
    if check_config_for_changes():
        log.warning(
            "❌ Example config has new entries, fill your config.yml and restart bot to apply update."
        )
        send_webhook("📝 Konfiguracja wymaga uzupełnienia, wymagany ręczny restart.")
        return
    restart_process()
