#!/usr/bin/env python3
import os
import pathlib
import yaml
from dotenv import load_dotenv
from netmiko import ConnectHandler
from jinja2 import Environment, FileSystemLoader

from logging_config import setup_logging  # <— new import

ROOT = pathlib.Path(__file__).resolve().parents[1]
INV_FILE = ROOT / "inventory" / "lab.yml"
TEMPLATES = ROOT / "templates"
OUT_DIR = ROOT / "configs_generated"
LOG_DIR = ROOT / "logs"
BACKUP_DIR = ROOT / "backups"

# Ensure dirs exist
OUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

load_dotenv(ROOT / ".env")

# Env
USERNAME = os.getenv("NET_USERNAME", "vyos")
PASSWORD = os.getenv("NET_PASSWORD", "")
SSH_KEY = os.getenv("NET_SSH_KEY", "")
SSH_PORT = int(os.getenv("NET_SSH_PORT", "22"))
COMMAND_TIMEOUT = int(os.getenv("COMMAND_TIMEOUT", "30"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Init logger
logger = setup_logging(LOG_DIR, LOG_LEVEL)
logger.info("Common initialized (inventory=%s)", INV_FILE)

def load_inventory() -> dict:
    with open(INV_FILE, "r") as f:
        data = yaml.safe_load(f)
    return data["devices"]

def conn_params_from_vars(vars: dict) -> dict:
    params = {
        "device_type": "vyos",
        "host": vars["host"],
        "username": USERNAME,
        "port": int(vars.get("ssh_port", SSH_PORT)),  # per-device override
        "timeout": COMMAND_TIMEOUT,
        "global_delay_factor": 1,
    }
    if SSH_KEY:
        params.update({"use_keys": True, "key_file": os.path.expanduser(SSH_KEY)})
    else:
        params["password"] = PASSWORD
    return params

def connect_from_vars(vars: dict):
    logger.debug("Connecting to %s:%s", vars["host"], vars.get("ssh_port", SSH_PORT))
    return ConnectHandler(**conn_params_from_vars(vars))

def render_device(name: str, vars: dict) -> pathlib.Path:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), trim_blocks=True, lstrip_blocks=True)
    ctx = {"inventory_hostname": name, **vars}
    chunks = []
    for tpl in ("base_vyos.j2", "ospf_vyos.j2", "bgp_vyos.j2"):
        if (TEMPLATES / tpl).exists():
            chunks.append(env.get_template(tpl).render(**ctx))
    body = "\n".join([c.strip() for c in chunks if c]).strip() + "\n"
    out_file = OUT_DIR / f"{name}.set"
    out_file.write_text(body)
    logger.info("Rendered %s", out_file)
    return out_file
