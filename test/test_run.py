import pytest

from vh.run import application


@pytest.fixture
def cli(loop, aiohttp_client):
    return loop.run_until_complete(aiohttp_client(application))


async def test_pong(cli):
    resp = await cli.get('/ping')
    assert resp.status == 200  # Ignore B101
