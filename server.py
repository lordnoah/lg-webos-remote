import asyncio
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from webos_wrapper import WebOSWrapper
from remote import KEY_MAP

app = FastAPI()

# Configuration
TV_IP = os.getenv("TV_IP", "192.168.1.29")
wrapper = WebOSWrapper(TV_IP)

class ActionRequest(BaseModel):
    action: str

class AppRequest(BaseModel):
    app_id: str

@app.on_event("startup")
async def startup_event():
    # Attempt to pair in the background so it doesn't block the server from starting
    async def bg_pair():
        try:
            print(f"Connecting to TV at {TV_IP}...")
            await wrapper.pair()
            print("Paired successfully!")
        except Exception as e:
            print(f"Startup pairing failed: {e}")
            # Will retry on command
            
    asyncio.create_task(bg_pair())

@app.post("/api/command")
async def send_command(req: ActionRequest):
    key = KEY_MAP.get(req.action, req.action)
    try:
        await wrapper.send_key(key)
        return {"status": "success", "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/launch")
async def launch_app(req: AppRequest):
    try:
        await wrapper._ensure_client()
        client = wrapper._client
        
        # aiopywebostv's launch_app or generic request
        if hasattr(client, "launch_app"):
            await client.launch_app(req.app_id)
        elif hasattr(client, "request"):
            # Raw RPC
            req_fn = getattr(client, "request")
            if asyncio.iscoroutinefunction(req_fn):
                await req_fn("ssap://com.webos.applicationManager/launch", {"id": req.app_id})
            else:
                req_fn("ssap://com.webos.applicationManager/launch", {"id": req.app_id})
        else:
            raise RuntimeError("launch_app not supported by this client library")
            
        return {"status": "success", "app_id": req.app_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve the PWA static files
app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
