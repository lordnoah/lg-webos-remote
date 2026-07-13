import asyncio
import logging
import re
from contextlib import asynccontextmanager

import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from webos_wrapper import WebOSWrapper
from remote import KEY_MAP
import wakeonlan

logger = logging.getLogger(__name__)

# Configuration
TV_IP = os.getenv("TV_IP", "192.168.1.29")
TV_MAC = os.getenv("TV_MAC", "60:75:6c:37:6a:58")
wrapper = WebOSWrapper(TV_IP)

# Allowlist of launchable app IDs
APP_ALLOWLIST = {
    "youtube.leanback.ytv.v1",
    "youtube.leanback.v4",
    "netflix",
    "amazon",
    "com.disney.disneyplus-prod",
    "com.viacom.paramountplus",
}

# Regex for validating app IDs that aren't in the allowlist
_APP_ID_RE = re.compile(r"^[a-zA-Z0-9._-]+$")


class ActionRequest(BaseModel):
    action: str


class AppRequest(BaseModel):
    app_id: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: attempt to pair in the background
    async def bg_pair():
        try:
            logger.info("Connecting to TV at %s...", TV_IP)
            await wrapper.pair()
            logger.info("Paired successfully!")
        except Exception:
            logger.exception("Startup pairing failed (will retry on command)")

    pair_task = asyncio.create_task(bg_pair())
    pair_task.add_done_callback(
        lambda t: t.result() if not t.cancelled() else None
    )
    yield
    # Shutdown: cancel pairing task if still running
    if not pair_task.done():
        pair_task.cancel()


app = FastAPI(lifespan=lifespan)


@app.post("/api/command")
async def send_command(req: ActionRequest):
    if req.action == "power" and TV_MAC:
        try:
            # Send to default port 9
            wakeonlan.send_magic_packet(TV_MAC)
            wakeonlan.send_magic_packet(TV_MAC, port=7)
            parts = TV_IP.split('.')
            if len(parts) == 4:
                subnet_bcast = f"{parts[0]}.{parts[1]}.{parts[2]}.255"
                wakeonlan.send_magic_packet(TV_MAC, ip_address=subnet_bcast)
                wakeonlan.send_magic_packet(TV_MAC, ip_address=subnet_bcast, port=7)
            logger.info("Sent WOL packets to %s (ports 7 & 9, broadcasts: %s)", TV_MAC, subnet_bcast if len(parts)==4 else '255.255.255.255')
        except Exception:
            logger.exception("Failed to send WOL packet")

    key = KEY_MAP.get(req.action)
    if key is None:
        raise HTTPException(status_code=400, detail=f"Unknown action: {req.action}")
    try:
        await wrapper.send_key(key)
        return {"status": "success", "key": key}
    except Exception as e:
        logger.warning(f"Initial send_key failed: {e}. Attempting to re-pair...")
        try:
            await wrapper.pair()
            await wrapper.send_key(key)
            return {"status": "success", "key": key, "note": "re-paired successfully"}
        except Exception:
            if req.action == "power":
                # If the TV was off, sending the key will fail, but WOL was sent.
                return {"status": "success", "key": key, "note": "WOL sent"}
            logger.exception("Failed to send command '%s'", req.action)
            raise HTTPException(status_code=500, detail="Command failed")


@app.post("/api/launch")
async def launch_app(req: AppRequest):
    # Validate app ID against allowlist or safe format
    if req.app_id not in APP_ALLOWLIST:
        if not _APP_ID_RE.match(req.app_id):
            raise HTTPException(status_code=400, detail="Invalid app ID format")

    try:
        await wrapper._ensure_client()
        client = wrapper._client

        if hasattr(client, "launch_app"):
            await client.launch_app(req.app_id)
        elif hasattr(client, "request"):
            req_fn = getattr(client, "request")
            if asyncio.iscoroutinefunction(req_fn):
                await req_fn("ssap://com.webos.applicationManager/launch", {"id": req.app_id})
            else:
                req_fn("ssap://com.webos.applicationManager/launch", {"id": req.app_id})
        else:
            raise RuntimeError("launch_app not supported by this client library")

        return {"status": "success", "app_id": req.app_id}
    except Exception as e:
        logger.warning(f"Initial launch failed: {e}. Attempting to re-pair...")
        try:
            await wrapper.pair()
            await wrapper._ensure_client()
            client = wrapper._client
            if hasattr(client, "launch_app"):
                await client.launch_app(req.app_id)
            elif hasattr(client, "request"):
                req_fn = getattr(client, "request")
                if asyncio.iscoroutinefunction(req_fn):
                    await req_fn("ssap://com.webos.applicationManager/launch", {"id": req.app_id})
                else:
                    req_fn("ssap://com.webos.applicationManager/launch", {"id": req.app_id})
            else:
                raise RuntimeError("launch_app not supported by this client library")
            return {"status": "success", "app_id": req.app_id, "note": "re-paired successfully"}
        except Exception:
            logger.exception("Failed to launch app '%s'", req.app_id)
            raise HTTPException(status_code=500, detail="Launch failed")


# Serve the PWA static files
app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
