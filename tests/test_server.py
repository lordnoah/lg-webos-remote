from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_command_endpoint():
    response = client.post("/api/command", json={"action": "vol_up"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "key": "VOLUMEUP"}

def test_launch_endpoint():
    response = client.post("/api/launch", json={"app_id": "youtube"})
    assert response.status_code == 200
    assert response.json() == {"status": "success", "app_id": "youtube"}
