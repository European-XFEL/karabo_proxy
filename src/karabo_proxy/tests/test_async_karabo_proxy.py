import os
import subprocess
from time import sleep

import pytest

from ..async_karabo_proxy import AsyncKaraboProxy
from ..schemas.web_proxy_responses import TopologyInfo
from ..sync_karabo_proxy import SyncKaraboProxy
from .mock_web_proxy import PORT_INVALID_MOCK, PORT_VALID_MOCK


@pytest.fixture(scope="module")
def web_proxy_mocks():
    mock_module_path = os.path.dirname(
        os.path.abspath(os.path.dirname(__file__)))
    proc_valid_mock = subprocess.Popen(
        ["python", "-m", "tests.mock_web_proxy"],
        cwd=mock_module_path)
    proc_invalid_mock = subprocess.Popen(
        ["python", "-m", "tests.mock_web_proxy", "--invalid"],
        cwd=mock_module_path)
    # The WebProxy mocks require some time to initialize and reach
    # the point when they can start accepting requests.
    sleep(2)
    yield
    proc_valid_mock.terminate()
    proc_invalid_mock.terminate()


@pytest.fixture(scope="module")
def valid_mock_async_cli():
    """Instantiantes an async client for the WebProxy mock that returns valid
    responses"""
    return AsyncKaraboProxy(f"http://localhost:{PORT_VALID_MOCK}")


@pytest.fixture(scope="module")
def invalid_mock_async_cli():
    """Instantiantes an async client for the WebProxy mock that returns
    invalid responses"""
    return AsyncKaraboProxy(f"http://localhost:{PORT_INVALID_MOCK}")


@pytest.fixture(scope="module")
def valid_mock_sync_cli():
    """Instantiantes a sync client for the WebProxy mock that returns valid
    responses"""
    return SyncKaraboProxy(f"http://localhost:{PORT_VALID_MOCK}")


@pytest.fixture(scope="module")
def invalid_mock_sync_cli():
    """Instantiantes a sync client for the WebProxy mock that returns
    invalid responses"""
    return SyncKaraboProxy(f"http://localhost:{PORT_INVALID_MOCK}")


@pytest.mark.asyncio
async def test_get_topology(web_proxy_mocks,
                            valid_mock_async_cli,
                            valid_mock_sync_cli,
                            invalid_mock_async_cli,
                            invalid_mock_sync_cli):
    # Checks that a correct async request to the valid mock succeeds
    topology = await valid_mock_async_cli.get_topology()
    assert (type(topology) is TopologyInfo)
    # Checks that a correct async request to the invalid mock fails due to the
    # invalid response
    with pytest.raises(RuntimeError, match="Invalid response format"):
        topology = await invalid_mock_async_cli.get_topology()

    # Checks that a correct sync request to the valid mock succeeds
    topology = valid_mock_sync_cli.get_topology()
    assert (type(topology) is TopologyInfo)
    # Checks that a correct sync request to the invalid mock fails due to the
    # invalid response
    with pytest.raises(RuntimeError, match="Invalid response format"):
        topology = invalid_mock_sync_cli.get_topology()
