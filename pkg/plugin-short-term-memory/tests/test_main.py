from fastapi.testclient import TestClient
from unittest.mock import patch
from api_server import app
import pytest
from memory_client import MemoryClient

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_get_memory_without_uuid(client):
    # Mock the return value of the MemoryClient's get_action method
    with patch.object(MemoryClient, 'get_action', return_value=({"ok": True, "message": "Success", "data": []}, 200, {})) as mock_get:
        # Make a request to the /get_memory endpoint
        response = client.get("/get_memory")
        # Assert that the response is as expected
        assert response.status_code == 200
        assert response.json() == {"ok": True, "message": "Success", "data": []}
        # Assert that the get_action method was called once
        mock_get.assert_called_once()
