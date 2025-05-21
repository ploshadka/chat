import pytest
from httpx import AsyncClient

from uuid import uuid4


@pytest.mark.asyncio
async def test_register_user():
    email = f"test_{uuid4().hex[:6]}@example.com"
    payload = {
        "email": email,
        "password": "test123",
        "name": "Test User"
    }

    async with AsyncClient(base_url="http://localhost:8000") as ac:
        res = await ac.post("/register", json=payload)

    assert res.status_code == 200
    data = res.json()
    assert data["email"] == email
    assert "id" in data

