import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture(autouse=True)
def mock_webos_wrapper(monkeypatch):
    """Mocks the WebOSWrapper methods so tests don't try to connect to a real TV."""
    monkeypatch.setattr("server.wrapper.pair", AsyncMock(return_value="mock-key"))
    monkeypatch.setattr("server.wrapper.send_key", AsyncMock())
    monkeypatch.setattr("server.wrapper._ensure_client", AsyncMock())

    # Mock the internal client for launch app
    class MockClient:
        async def launch_app(self, app_id):
            pass

    monkeypatch.setattr("server.wrapper._client", MockClient())

    # Mock wakeonlan so no real UDP packets are sent
    monkeypatch.setattr("server.wakeonlan.send_magic_packet", MagicMock())

