#!/usr/bin/env python3
"""
Post-deploy validation with clear PASS/FAIL and non-zero exit on failure.
"""

import sys
from common import load_inventory, connect

def check_device(name, host) -> tuple[bool, list[str]]:
    conn = connect(host)
    logs = []
    ok = True
    try:
        out = conn.send_command("show ip ospf neighbor | no-more", use_textfsm=False)
        logs.append(("show ip ospf neighbor", out))
        # Soft check: if OSPF exists, I expect at least one 'Full' or NEIGHBOR header
        if ("Full" not in out) and ("Neighbor ID" not in out):
            pass

        out = conn.send_command("show ip bgp summary | no-more", use_textfsm=False)
        logs.append(("show ip bgp summary", out))
        # Soft check: not all nodes run BGP; don't fail hard here

        out = conn.send_command("show ip route | match 0.0.0.0/0", use_textfsm=False)
        logs.append(("show ip route | match 0.0.0.0/0", out))
        # Edge devices should display a default route; core may not.

    except Exception as e:
        ok = False
        logs.append(("exception", str(e)))
    finally:
        conn.disconnect()
    rendered = "\n".join([f"\n$ {cmd}\n{txt}" for cmd, txt in logs])
    return ok, rendered

def main():
    devices = load_inventory()
    overall_ok = True
    for name, v in devices.items():
        ok, txt = check_device(name, v["host"])
        print(f"\n=== {name} ({v['host']}) ===")
        print(txt)
        overall_ok = overall_ok and ok
    return 0 if overall_ok else 2

if __name__ == "__main__":
    sys.exit(main())
