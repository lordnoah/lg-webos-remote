"""Wrapper around aiopywebostv for pairing and sending basic remote keys.

This is a best-effort compatibility layer: it attempts several common
method names used by different webOS client libraries so the CLI can
work across environments. It requires `aiopywebostv` to be installed.
"""

from __future__ import annotations

import asyncio
import json
from typing import Optional


class WebOSWrapper:
    def __init__(self, host: str, client_name: str = "LG Remote Prototype"):
        self.host = host
        self.client_name = client_name
        self._client = None

    async def _ensure_client(self):
        if self._client:
            return
        try:
            import aiowebostv as aw
        except Exception as exc:  # pragma: no cover - runtime dependency
            raise RuntimeError("aiowebostv is required. Install with `pip install aiowebostv`") from exc

        # Try several possible client class names used by different versions
        Client = None
        for name in ("WebOsClient", "WebOSClient", "WebOsClient", "WebOSClient", "Client"):
            Client = getattr(aw, name, None)
            if Client:
                break

        if Client is None:
            # Maybe the package exposes a factory
            Client = getattr(aw, "create_client", None)

        if Client is None:
            raise RuntimeError("aiowebostv installed but no expected client class found")

        # Instantiate client
        try:
            self._client = Client(self.host)
        except TypeError:
            # some constructors take (host, port)
            self._client = Client(self.host, 3000)

    async def pair(self, timeout: int = 60) -> str:
        """Run pairing flow. Returns a client key if obtained.

        The exact pairing API differs between libraries; we attempt several
        common method names. If the library initiates a PIN-based pairing,
        the TV will show a PIN and the user should confirm it on the TV.
        """
        await self._ensure_client()
        client = self._client

        # Try connect/open method
        for conn_name in ("connect", "open", "start"):
            fn = getattr(client, conn_name, None)
            if fn:
                if asyncio.iscoroutinefunction(fn):
                    await fn()
                else:
                    fn()
                break

        # Try a variety of pairing method names
        pair_methods = ("pair", "request_pairing", "request_pairing_key", "register", "request_register")
        paired_key: Optional[str] = None
        for name in pair_methods:
            fn = getattr(client, name, None)
            if not fn:
                continue
            try:
                if asyncio.iscoroutinefunction(fn):
                    res = await fn(self.client_name) if fn.__code__.co_argcount > 0 else await fn()
                else:
                    res = fn(self.client_name) if fn.__code__.co_argcount > 0 else fn()
                # Try to extract a client key from common response shapes
                if isinstance(res, dict):
                    for k in ("client_key", "client-key", "clientKey", "clientkey"):
                        if k in res:
                            paired_key = res[k]
                            break
                elif isinstance(res, str):
                    paired_key = res
                # Some libraries store the key on the client object
                if not paired_key:
                    for attr in ("client_key", "clientKey", "key", "_client_key"):
                        if hasattr(client, attr):
                            paired_key = getattr(client, attr)
                            break
                if paired_key:
                    break
            except Exception:
                # ignore and try next method
                continue

        if not paired_key:
            raise RuntimeError("Pairing failed or client key not returned by library; check TV for PIN and library docs")

        # Normalize to string
        if isinstance(paired_key, bytes):
            paired_key = paired_key.decode("utf-8")

        # Persist key if client supports storing
        try:
            if hasattr(client, "store_client_key"):
                store = getattr(client, "store_client_key")
                if asyncio.iscoroutinefunction(store):
                    await store(paired_key)
                else:
                    store(paired_key)
        except Exception:
            pass

        return str(paired_key)

    async def send_key(self, key: str) -> None:
        """Send a simple remote key (UP/DOWN/LEFT/RIGHT/ENTER/VOLUMEUP/VOLUMEDOWN/MUTE/POWER).

        This method tries several action APIs commonly found on webOS clients.
        """
        await self._ensure_client()
        client = self._client

        # Try a few common send key methods
        send_names = ("button", "key", "send_key", "send_button", "press")
        for name in send_names:
            fn = getattr(client, name, None)
            if not fn:
                continue
            try:
                if asyncio.iscoroutinefunction(fn):
                    await fn(key)
                else:
                    fn(key)
                return
            except Exception:
                continue

        # Try a generic 'request' method (some clients expose raw RPC)
        req = getattr(client, "request", None)
        if req:
            try:
                if asyncio.iscoroutinefunction(req):
                    await req("ssap://com.webos.service.ime/button", {"name": key})
                else:
                    req("ssap://com.webos.service.ime/button", {"name": key})
                return
            except Exception:
                pass

        raise RuntimeError("Unable to send key: no compatible method found on aiopywebostv client")
