from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_command_endpoint():
    response = client.post("/api/command", json={"action": "vol_up"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "key": "VOLUMEUP"}

def test_command_unknown_action_rejected():
    response = client.post("/api/command", json={"action": "self_destruct"})
    assert response.status_code == 400
    assert "Unknown action" in response.json()["detail"]

def test_command_empty_action_rejected():
    response = client.post("/api/command", json={"action": ""})
    assert response.status_code == 400

def test_launch_endpoint():
    response = client.post("/api/launch", json={"app_id": "youtube.leanback.v4"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "app_id": "youtube.leanback.v4"}

def test_launch_allowlisted_app():
    response = client.post("/api/launch", json={"app_id": "netflix"})
    assert response.status_code == 200

def test_launch_valid_format_not_in_allowlist():
    """App IDs with safe format are still accepted even if not in the allowlist."""
    response = client.post("/api/launch", json={"app_id": "com.example.newapp"})
    assert response.status_code == 200

def test_launch_invalid_format_rejected():
    """App IDs with dangerous characters are rejected."""
    response = client.post("/api/launch", json={"app_id": "../../etc/passwd"})
    assert response.status_code == 400
    assert "Invalid app ID" in response.json()["detail"]

def test_launch_empty_app_id_rejected():
    response = client.post("/api/launch", json={"app_id": ""})
    assert response.status_code == 400

def test_launch_special_chars_rejected():
    response = client.post("/api/launch", json={"app_id": "app; rm -rf /"})
    assert response.status_code == 400

def test_command_error_does_not_leak_details(monkeypatch):
    """Ensure internal exception messages are not returned to the client."""
    from unittest.mock import AsyncMock
    monkeypatch.setattr(
        "server.wrapper.send_key",
        AsyncMock(side_effect=RuntimeError("secret internal error at /opt/lg-remote/webos.py:42"))
    )
    monkeypatch.setattr(
        "server.wrapper.pair",
        AsyncMock(side_effect=RuntimeError("pair also fails"))
    )
    response = client.post("/api/command", json={"action": "up"})
    assert response.status_code == 500
    assert "secret" not in response.json()["detail"]
    assert response.json()["detail"] == "Command failed"


def test_power_command_sends_wol(monkeypatch):
    """Power command should send WOL magic packets."""
    from unittest.mock import MagicMock
    mock_wol = MagicMock()
    monkeypatch.setattr("server.wakeonlan.send_magic_packet", mock_wol)
    response = client.post("/api/command", json={"action": "power"})
    assert response.status_code == 200
    assert mock_wol.call_count >= 1


def test_power_command_succeeds_even_when_tv_unreachable(monkeypatch):
    """Power command should return success (WOL sent) even if the TV is off."""
    from unittest.mock import AsyncMock, MagicMock
    monkeypatch.setattr(
        "server.wrapper.send_key",
        AsyncMock(side_effect=ConnectionError("TV is off"))
    )
    monkeypatch.setattr(
        "server.wrapper.pair",
        AsyncMock(side_effect=ConnectionError("TV is off"))
    )
    mock_wol = MagicMock()
    monkeypatch.setattr("server.wakeonlan.send_magic_packet", mock_wol)
    response = client.post("/api/command", json={"action": "power"})
    assert response.status_code == 200
    assert response.json()["note"] == "WOL sent"
    assert mock_wol.call_count >= 1


def test_non_power_command_does_not_send_wol(monkeypatch):
    """Non-power commands should not send WOL packets."""
    from unittest.mock import MagicMock
    mock_wol = MagicMock()
    monkeypatch.setattr("server.wakeonlan.send_magic_packet", mock_wol)
    response = client.post("/api/command", json={"action": "vol_up"})
    assert response.status_code == 200
    assert mock_wol.call_count == 0

