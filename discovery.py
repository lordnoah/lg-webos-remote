#!/usr/bin/env python3
"""Simple SSDP discovery to find LG webOS TVs on the local network."""

import socket
import time
from urllib.parse import urlparse

SSDP_ADDR = ("239.255.255.250", 1900)
MSEARCH = """M-SEARCH * HTTP/1.1\r
HOST: 239.255.255.250:1900\r
MAN: "ssdp:discover"\r
MX: 3\r
ST: ssdp:all\r
\r
"""


def discover(timeout: int = 3):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)

    sock.sendto(MSEARCH.encode("utf-8"), SSDP_ADDR)

    found = {}
    start = time.time()
    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            break
        text = data.decode("utf-8", errors="ignore")
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        headers = {}
        for ln in lines[1:]:
            if ":" in ln:
                k, v = ln.split(":", 1)
                headers[k.strip().upper()] = v.strip()

        location = headers.get("LOCATION") or headers.get("HOST")
        server = headers.get("SERVER", "")
        usn = headers.get("USN", f"{addr[0]}")

        # Use LOCATION header or response address
        ip = None
        if location:
            try:
                parsed = urlparse(location)
                if parsed.hostname:
                    ip = parsed.hostname
            except Exception:
                ip = None

        if not ip:
            ip = addr[0]

        found[ip] = {"ip": ip, "server": server, "usn": usn, "headers": headers}

        # timeout guard
        if time.time() - start > timeout:
            break

    sock.close()
    return list(found.values())


if __name__ == "__main__":
    print("Discovering devices (3s)...")
    devs = discover(3)
    if not devs:
        print("No devices found. Ensure you're on the same network as the TV.")
    else:
        print("Found devices:")
        for d in devs:
            print(f"- {d['ip']}  server={d.get('server')}")
