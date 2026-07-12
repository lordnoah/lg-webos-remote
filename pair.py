#!/usr/bin/env python3
"""Pairing CLI for webOS TVs using the wrapper.

Usage:
  python3 pair.py <TV_IP> [key_file]

If a client key is returned it will be saved to the provided key_file
or `webos_client_key.txt` by default.
"""

import asyncio
import sys
from webos_wrapper import WebOSWrapper


async def run(ip: str, key_file: str = "webos_client_key.txt"):
    w = WebOSWrapper(ip)
    try:
        print(f"Attempting pairing with {ip}. Confirm PIN on TV if prompted.")
        key = await w.pair()
        print("Paired successfully. Client key:", key)
        with open(key_file, "w") as fh:
            fh.write(key)
        print(f"Saved client key to {key_file}")
    except Exception as exc:
        print("Pairing failed:", exc)
        print("If the TV displayed a PIN, re-run pairing and accept it on the TV.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pair.py <TV_IP> [key_file]")
        sys.exit(1)
    ip = sys.argv[1]
    key_file = sys.argv[2] if len(sys.argv) > 2 else "webos_client_key.txt"
    asyncio.run(run(ip, key_file))
