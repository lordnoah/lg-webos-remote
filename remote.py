"""Simple remote API that wraps `WebOSWrapper` for common actions."""

from __future__ import annotations

import asyncio
from webos_wrapper import WebOSWrapper


KEY_MAP = {
    "up": "UP",
    "down": "DOWN",
    "left": "LEFT",
    "right": "RIGHT",
    "enter": "ENTER",
    "back": "BACK",
    "home": "HOME",
    "vol_up": "VOLUMEUP",
    "vol_down": "VOLUMEDOWN",
    "mute": "MUTE",
    "power": "POWER",
}


class Remote:
    def __init__(self, host: str):
        self.host = host
        self._wrapper = WebOSWrapper(host)

    async def send(self, action: str):
        key = KEY_MAP.get(action, action)
        await self._wrapper.send_key(key)


def quick_command(host: str, action: str):
    r = Remote(host)
    return asyncio.run(r.send(action))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 remote.py <TV_IP> <action>")
        print("Actions:", ", ".join(KEY_MAP.keys()))
        raise SystemExit(1)

    host = sys.argv[1]
    action = sys.argv[2]
    quick_command(host, action)
