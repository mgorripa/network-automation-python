# Automated Network Configuration Deployment (Python + VyOS)

This project demonstrates how I built an automated network configuration system for a simulated multi-router VyOS lab.  
The goal was to move away from manual CLI work and adopt modern infrastructure-as-code practices:
- Configurations are templated in Jinja2.  
- Device variables live in a structured inventory.  
- Python scripts handle config generation, backups, diffs, and deployments.  
- Logs and backups are automatically managed for traceability.  
- CI/CD validates configs before anything touches the lab.

---

## Project Overview
- Problem I solved: Manual configuration across multiple routers is error-prone and inconsistent.  
- My approach: Automate the entire config lifecycle — generation, validation, deployment, and rollback.  
- Technologies used:
  - Python (Netmiko, Jinja2, PyYAML, dotenv, Rich)
  - VyOS routers running in VirtualBox/GNS3
  - GitHub Actions for CI/CD checks
- Key features:
  - Generate configs from templates and inventory
  - Run diffs between intended vs. running configs
  - Backup current configs before deployment
  - Push only missing commands (idempotent)
  - Parallel deployments (async workers)
  - Post-deploy validation (OSPF neighbors, BGP sessions, default routes)
  - Centralized logging with rotation
  - Automatic cleanup of old logs/backups

---

## Repository Structure
network-automation-python/
├── README.md # Project documentation (this file)
├── .env.example # Example environment variables (copy to .env)
├── inventory/ # YAML inventory (device definitions, ASNs, IPs)
│ └── lab.yml
├── templates/ # Jinja2 templates (base, OSPF, BGP)
│ ├── base_vyos.j2
│ ├── ospf_vyos.j2
│ └── bgp_vyos.j2
├── configs/ # Static sample configs (if needed)
├── configs_generated/ # Auto-generated configs (gitignored)
├── backups/ # Device backups with timestamp (gitignored)
├── logs/ # Rotating logs + per-device validation output
├── scripts/ # Python automation scripts
│ ├── common.py
│ ├── deploy_async.py
│ ├── diff.py
│ ├── backup.py
│ ├── validate.py
│ ├── cleanup.py
│ └── logging_config.py
└── .github/workflows/ci.yml # CI/CD pipeline (lint + config build)


---

## Prerequisites
- Python 3.9+  
- Virtual environment (`python -m venv .venv`)  
- Dependencies from `requirements.txt`:
      `pip install -r requirements.txt`
- VyOS routers running in VirtualBox or GNS3  
- SSH enabled on all routers (`set service ssh port 22`)  
- Unique management IPs reachable from the automation host

---

## Environment Setup
1. Copy the example env file:
 ```bash
 cp .env.example .env
```
2. Edit `.env` with your credentials (password or SSH key).
3. Verify inventory file (`inventory/lab.yml`) has correct IPs and ASNs.

---

## Workflow

The network automation process is divided into a clear, six-step workflow:

1.  **Generate Configs**
    ```bash
    python scripts/deploy_async.py --generate-only
    ```
    This script generates `.set` configuration files in the `configs_generated/` directory, pulling data from an inventory and applying it to predefined templates.

2.  **Compare Intended vs. Running Configs**
    ```bash
    python scripts/diff.py
    ```
    This command shows a line-by-line comparison between the newly generated configurations and the configurations currently active on the network devices, allowing for a clear "what-if" analysis before deployment.

3.  **Take Backups**
    ```bash
    python scripts/backup.py
    ```
    Before any changes are pushed, this script takes a backup of the current device configurations, saving them to the `backups/` directory with a timestamp. This provides a critical safety net for easy rollback.

4.  **Deploy Changes (Parallel & Idempotent)**
    ```bash
    python scripts/deploy_async.py --max-workers 6
    ```
    This is the core deployment script. It connects to each router and pushes **only the missing commands**, making the operation idempotent. It supports concurrent connections with a configurable number of workers for faster deployment across multiple devices.

5.  **Validate Post-Deploy**
    ```bash
    python scripts/validate.py
    ```
    After deployment, this script verifies that the intended state has been achieved by checking for OSPF adjacencies, BGP sessions, and default routes.

6.  **Cleanup Old Logs/Backups**
    ```bash
    python scripts/cleanup.py
    ```
    This script helps maintain a tidy repository by removing old log files and backups that are older than the retention period defined in the `.env` file.

---

## CI/CD (GitHub Actions)

This project is integrated with GitHub Actions to automate key tasks on every push or pull request:

* **Lints Python code** with `flake8`.
* **Generates configs** in a dry-run mode.
* **Runs unit tests** with `pytest`.
* **Uploads `configs_generated/`** as build artifacts.

---

## Results and Learnings

* **Reduced manual CLI work** by more than 80%, demonstrating the power of network automation.
* **Practiced building idempotent, safe automation**, similar to enterprise-grade tools like Ansible or Puppet.
* **Integrated network automation** with modern CI/CD pipelines.
* **Designed for extensibility**, allowing for easy future integration of features like BFD or NetBox.
* **Combined network engineering fundamentals with Python development skills.**

---

## Future Improvements

* Add `commit-confirm` rollback logic for VyOS devices.
* Extend templates to support ACLs, route-maps, and summarization.
* Replace Netmiko with `scrapli` or `asyncssh` for faster connections.
* Tie into a source-of-truth (e.g., NetBox) to manage inventory.

---

## License

This project is licensed under the MIT License. Feel free to use it as a reference or template for your own projects. Attribution is appreciated.
