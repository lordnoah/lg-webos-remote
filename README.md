# WebOS Smart Remote PWA

A mobile-first, Progressive Web App (PWA) and Python backend to control LG WebOS Smart TVs over your local network. 

This project provides a premium, 3D glassmorphism UI that looks and feels like a physical remote, right from your phone's home screen.

## Architecture

This project is split into a frontend PWA and a Python Flask backend.

### Frontend (PWA)
Located in the `public/` directory, the frontend is built with pure HTML, CSS, and vanilla JavaScript for maximum performance and no build steps.
- **`index.html` & `style.css`**: Provides a stunning, 3D glassmorphism UI imitating a physical LG remote. Features a directional pad, volume rocker, and quick-launch app buttons (Netflix, YouTube TV, Prime Video, etc.).
- **`app.js`**: Handles user interactions, triggers mobile haptic feedback (`navigator.vibrate`), and fires async REST requests to the backend.
- **`manifest.json` & `sw.js`**: Service worker and manifest allowing you to install the remote directly to your iOS or Android home screen as a standalone app.

### Backend (Python)
The backend acts as a bridge between the HTTP frontend and the WebSocket-based WebOS TV.
- **`server.py`**: A Flask HTTP server that serves the static frontend files and exposes `/api/command` and `/api/launch` REST endpoints.
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
   This will build the Python image, mount the `public/` directory, and expose the Flask server on port `5001`.

3. **Install on your Phone**
   - Open Safari (iOS) or Chrome (Android).
   - Navigate to `http://<YOUR_SERVER_IP>:5001`.
   - Tap "Share" -> "Add to Home Screen".
   - You now have a full-screen, native-feeling remote app on your phone!

## Modifying the UI

You can update the frontend without restarting the Docker container. Simply edit the files in the `public/` directory, and because it is mounted as a volume in `docker-compose.yml`, the changes will be reflected immediately upon refreshing the app.
