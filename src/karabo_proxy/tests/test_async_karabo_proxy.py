import asyncio

import pytest
import pytest_asyncio

from ..async_karabo_proxy import AsyncKaraboProxy
from ..schemas.web_proxy_responses import TopologyInfo
from .mock_web_proxy import (
    PORT_INVALID_MOCK, PORT_VALID_MOCK, run_invalid_mock, run_valid_mock)


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    loop = asyncio.get_event_loop()
    yield loop
    # Note: the aiohttp server does not close gracefully, allowing a warning
    # about pending tasks being destroyed at the end of the test. The problem
    # is a known issue of aiohttp and is expected to be solved on an upcoming
    # version 4.0: https://github.com/aio-libs/aiohttp/issues/4408.
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def valid_mock_cli():
    """Instantiantes a client for the WebProxy mock that returns valid
    responses (after launching the mock, a web server application)"""
    await run_valid_mock()
    return AsyncKaraboProxy(f"http://localhost:{PORT_VALID_MOCK}")


@pytest_asyncio.fixture(scope="module")
async def invalid_mock_cli():
    """Instantiantes a client for the WebProxy mock that returns invalid
    responses (after launching the mock, a web server application)"""
    await run_invalid_mock()
    return AsyncKaraboProxy(f"http://localhost:{PORT_INVALID_MOCK}")


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_get_topology(event_loop, valid_mock_cli, invalid_mock_cli):
    # Checks that a correct request to the valid mock succeeds
    topology = await valid_mock_cli.get_topology()
    assert (type(topology) is TopologyInfo)
    # Checks that a correct request to the invalid mock fails due to the
    # invalid response
    with pytest.raises(RuntimeError, match="Invalid response format"):
        topology = await invalid_mock_cli.get_topology()
