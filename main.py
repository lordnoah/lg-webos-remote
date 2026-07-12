#!/usr/bin/env python3
"""CLI scaffold for LG webOS remote prototype.

Steps:
- Run `discovery.py` to find your TV's IP.
- Provide the IP to this script. Next step would be to implement pairing + commands using `aiopywebostv`.
"""

import sys
import subprocess
from discovery import discover


def ensure_deps():
    try:
        import aiopywebostv  # type: ignore
        print("aiopywebostv available — ready to implement pairing/control.")
    except Exception:
        print("aiopywebostv not installed. To install run:")
        print("  pip install aiopywebostv")


def main():
    print("Discovering LG TVs on the network...")
    devs = discover(3)
    if not devs:
        print("No devices found. Try running discovery again or check network.")
        sys.exit(1)

    for i, d in enumerate(devs, 1):
        print(f"[{i}] {d['ip']}  server={d.get('server')}")

    choice = input("Select device number (or enter IP): ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if idx < 0 or idx >= len(devs):
            print("Invalid selection")
            sys.exit(1)
        ip = devs[idx]['ip']
    else:
        ip = choice

    print(f"Selected TV IP: {ip}")
    ensure_deps()

    print("\nNext steps:")
    print(f"- Run a pairing script using `aiopywebostv` targeting {ip}.")
    print("- After pairing, implement navigation (UP/DOWN/LEFT/RIGHT/ENTER), volume, and power commands.")


if __name__ == "__main__":
    main()
