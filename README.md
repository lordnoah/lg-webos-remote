# WebOS Smart Remote PWA

A mobile-first, Progressive Web App (PWA) and Python backend to control LG WebOS Smart TVs over your local network. 

This project provides a premium, 3D glassmorphism UI that looks and feels like a physical remote, right from your phone's home screen.

## Architecture

This project is split into a frontend PWA and a Python FastAPI backend.

### Frontend (PWA)
Located in the `public/` directory, the frontend is built with pure HTML, CSS, and vanilla JavaScript for maximum performance and no build steps.
- **`index.html` & `style.css`**: Provides a stunning, 3D glassmorphism UI imitating a physical LG remote. Features a directional pad, volume rocker, and quick-launch app buttons (Netflix, YouTube TV, Prime Video, etc.).
- **`app.js`**: Handles user interactions, triggers mobile haptic feedback (`navigator.vibrate`), and fires async REST requests to the backend. It also utilizes the Fullscreen API to provide a native app experience on Android without requiring an HTTPS certificate.
- **`manifest.json` & `sw.js`**: Service worker and manifest allowing you to install the remote directly to your iOS or Android home screen as a standalone app.

### Backend (Python)
The backend acts as a bridge between the HTTP frontend and the WebSocket-based WebOS TV.
- **`server.py`**: A FastAPI HTTP server that serves the static frontend files and exposes `/api/command` and `/api/launch` REST endpoints. Includes Wake-on-LAN (WOL) support to power on the TV from standby, and auto-reconnect logic so the server recovers gracefully if it starts while the TV is off.
- **`webos_wrapper.py`**: An asynchronous wrapper around the `aiopywebostv` library. It maintains a persistent WebSocket connection to the LG TV, translating incoming REST API calls into WebOS commands (volume control, D-pad navigation, app launching, etc.).
- **`discovery.py` & `pair.py`**: Helper scripts used to discover the LG TV on the local network and perform the initial pairing handshake.

## Installation & Deployment

The easiest way to run the backend is via Docker on an always-on device in your home network (like a Raspberry Pi or Linux server).

1. **Discover & Pair your TV**
   Before running the server, you need to pair with your TV to get a client key.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python3 pair.py <YOUR_TV_IP>
   ```
   *Note: Accept the pairing prompt on your TV screen. The script will save the client key to a local file.*

2. **Run with Docker Compose**
   Once paired, you can spin up the server.
   ```bash
   sudo docker-compose up -d
   ```
   This will build the Python image, mount the `public/` directory, and expose the FastAPI server on port `8000`.

   > **Note:** The Docker Compose file uses `network_mode: "host"` so that Wake-on-LAN broadcast packets can reach the TV on the local network. The server binds to port `8000` directly on the host.

3. **Configure your TV for Remote Power-On**
   To allow the web remote to turn the TV on from standby:
   - Go to **Settings > General > Always Ready** and select **"Always Ready without wallpaper"**. This keeps the network interface alive in standby so the TV can receive Wake-on-LAN packets.
   - Go to **Settings > General > Devices > TV Management > TV On With Mobile** and enable **"Turn on via Wi-Fi"**.
   - The `TV_MAC` environment variable in `docker-compose.yml` should match your TV's **Ethernet MAC address** (found in Settings > Network > Wired Connection).

4. **Install on your Phone**
   - Open Safari (iOS) or Chrome (Android).
   - Navigate to `http://<YOUR_SERVER_IP>:8000`.
   - Tap "Share" -> "Add to Home Screen".
   - You now have a full-screen, native-feeling remote app on your phone!

## Modifying the UI

You can update the frontend without restarting the Docker container. Simply edit the files in the `public/` directory, and because it is mounted as a volume in `docker-compose.yml`, the changes will be reflected immediately upon refreshing the app.

## Testing

The codebase includes a comprehensive `pytest` suite for the Python backend. The tests use `httpx` to mock requests and a mocked `WebOSWrapper` to ensure no connections are made to your actual TV during testing.

To run the tests:
```bash
source .venv/bin/activate
pip install -r requirements.txt
pytest tests/
```
