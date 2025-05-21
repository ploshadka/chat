import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_group():
    """ Группа появится в БД """
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        res = await ac.post("/groups", json={
            "title": "Test Group From Pytest",
            "creator_id": 1,
            "member_ids": [1, 2]
        })

    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Test Group From Pytest"
    assert set(data["member_ids"]) >= {1, 2}
