import os
import subprocess
from time import sleep

import pytest

from ..async_karabo_proxy import AsyncKaraboProxy
from ..data.device_config import PropertyInfo
from ..data.topology import DevicesInfo, TopologyInfo
from ..sync_karabo_proxy import SyncKaraboProxy
from .mock_web_proxy import (
    DEVICE_GET_CONFIGURATION_VALID, PORT_INVALID_MOCK, PORT_VALID_MOCK)


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
    sleep(3)
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
    assert type(topology) is TopologyInfo
    # Checks that a correct async request to the invalid mock fails due to the
    # invalid response
    with pytest.raises(RuntimeError, match="Invalid response format"):
        topology = await invalid_mock_async_cli.get_topology()

    # Checks that a correct sync request to the valid mock succeeds
    topology = valid_mock_sync_cli.get_topology()
    assert type(topology) is TopologyInfo
    # Checks that a correct sync request to the invalid mock fails due to the
    # invalid response
    with pytest.raises(RuntimeError, match="Invalid response format"):
        topology = invalid_mock_sync_cli.get_topology()


@pytest.mark.asyncio
async def test_get_devices(web_proxy_mocks,
                           valid_mock_async_cli,
                           valid_mock_sync_cli,
                           invalid_mock_async_cli,
                           invalid_mock_sync_cli):
    # Checks that a correct async request to the valid mock succeeds
    devices = await valid_mock_async_cli.get_devices()
    assert type(devices) is DevicesInfo
    # Checks that a correct async request to the invalid mock fails due to the
    # invalid response
    with pytest.raises(RuntimeError, match="Invalid response format"):
        devices = await invalid_mock_async_cli.get_devices()

    # Checks that a correct sync request to the valid mock succeeds
    devices = valid_mock_sync_cli.get_devices()
    assert type(devices) is DevicesInfo
    # Checks that a correct sync request to the invalid mock fails due to the
    # invalid response
    with pytest.raises(RuntimeError, match="Invalid response format"):
        devices = invalid_mock_sync_cli.get_devices()


@pytest.mark.asyncio
async def test_get_device_configuration(web_proxy_mocks,
                                        valid_mock_async_cli,
                                        valid_mock_sync_cli,
                                        invalid_mock_async_cli,
                                        invalid_mock_sync_cli):
    # Checks that a correct async request to the valid mock succeeds
    config = await valid_mock_async_cli.get_device_configuration("any_works")
    assert type(config) is dict
    assert "_deviceId_" in config
    assert config["_deviceId_"]["value"] in DEVICE_GET_CONFIGURATION_VALID
    # Checks that a correct async request to the invalid mock fails
    with pytest.raises(RuntimeError,
                       match="Error getting device configuration"):
        config = await invalid_mock_async_cli.get_device_configuration(
            "none_works")

    # Checks that a correct sync request to the valid mock succeeds
    config = valid_mock_sync_cli.get_device_configuration("any_works")
    assert type(config) is dict
    assert "_deviceId_" in config
    assert config["_deviceId_"]["value"] in DEVICE_GET_CONFIGURATION_VALID
    # Checks that a correct async request to the invalid mock fails with an
    # error that the queried device is not available
    with pytest.raises(RuntimeError,
                       match="Error getting device configuration"):
        config = invalid_mock_sync_cli.get_device_configuration("none_works")


@pytest.mark.asyncio
async def test_get_config_path(web_proxy_mocks,
                               valid_mock_async_cli,
                               valid_mock_sync_cli,
                               invalid_mock_async_cli,
                               invalid_mock_sync_cli):
    # Checks that a correct async request to the valid mock succeeds
    prop = await valid_mock_async_cli.get_device_config_path("any_works",
                                                             "prop")
    assert type(prop) is PropertyInfo
    # Checks that a correct async request to the invalid mock fails
    with pytest.raises(RuntimeError,
                       match="Invalid response format"):
        await invalid_mock_async_cli.get_device_config_path("none_works",
                                                            "prop")

    # Checks that a correct sync request to the valid mock succeeds
    prop = valid_mock_sync_cli.get_device_config_path("any_works", "prop")
    assert type(prop) is PropertyInfo
    # Checks that a correct async request to the invalid mock fails
    with pytest.raises(RuntimeError,
                       match="Invalid response format"):
        invalid_mock_sync_cli.get_device_config_path("none_works", "prop")


@pytest.mark.asyncio
async def test_set_device_configuration(web_proxy_mocks,
                                        valid_mock_async_cli,
                                        valid_mock_sync_cli,
                                        invalid_mock_async_cli,
                                        invalid_mock_sync_cli):
    # Checks that a correct async request to the valid mock succeeds
    result = await valid_mock_async_cli.set_device_configuration(
        "any_works", {"a_property": 120, "another_property": "abc"})
    assert result.success
    assert result.reason == ""
    # Checks that a correct async request to the invalid mock fails
    result = await invalid_mock_async_cli.set_device_configuration(
        "none_works", {"a_property": 120})
    assert not result.success
    assert result.reason.startswith("Lacking valid access_token")

    # Checks that a correct sync request to the valid mock succeeds
    result = valid_mock_sync_cli.set_device_configuration(
        "any_works", {"a_property": 120, "another_property": "abc"})
    assert result.success
    assert result.reason == ""
    # Checks that a correct sync request to the invalid mock fails
    result = invalid_mock_sync_cli.set_device_configuration(
        "none_works", {"a_property": 120})
    assert not result.success
    assert result.reason.startswith("Lacking valid access_token")


@pytest.mark.asyncio
async def test_set_config_path(web_proxy_mocks,
                               valid_mock_async_cli,
                               valid_mock_sync_cli,
                               invalid_mock_async_cli,
                               invalid_mock_sync_cli):
    # Checks that a correct async request to the valid mock succeeds
    result = await valid_mock_async_cli.set_device_config_path("any_works",
                                                               "prop", 78)
    assert result.success
    assert result.reason == ""
    # Checks that a correct async request to the invalid mock fails
    result = await invalid_mock_async_cli.set_device_config_path("none_works",
                                                                 "prop", 78)
    assert not result.success
    assert result.reason.startswith("Lacking valid access_token")

    # Checks that a correct sync request to the valid mock succeeds
    result = valid_mock_sync_cli.set_device_config_path("any_works",
                                                        "prop", 78)
    assert result.success
    assert result.reason == ""
    # Checks that a correct sync request to the invalid mock fails
    result = invalid_mock_sync_cli.set_device_config_path("none_works",
                                                          "prop", 78)
    assert not result.success
    assert result.reason.startswith("Lacking valid access_token")


@pytest.mark.asyncio
async def test_get_device_schema(web_proxy_mocks,
                                 valid_mock_async_cli,
                                 valid_mock_sync_cli,
                                 invalid_mock_async_cli,
                                 invalid_mock_sync_cli):
    # Checks that a correct async request to the valid mock succeeds
    schema = await valid_mock_async_cli.get_device_schema("any_works")
    assert type(schema) is dict
    # Checks that a correct async request to the invalid mock fails
    with pytest.raises(RuntimeError,
                       match="Device not online"):
        await invalid_mock_async_cli.get_device_schema("none_works")

    # Checks that a correct sync request to the valid mock succeeds
    schema = valid_mock_sync_cli.get_device_schema("any_works")
    assert type(schema) is dict
    # Checks that a correct async request to the invalid mock fails
    with pytest.raises(RuntimeError,
                       match="Device not online"):
        invalid_mock_sync_cli.get_device_schema("none_works")


@pytest.mark.asyncio
async def test_execute_slot(web_proxy_mocks,
                            valid_mock_async_cli,
                            valid_mock_sync_cli,
                            invalid_mock_async_cli,
                            invalid_mock_sync_cli):
    # Checks that a correct async request to the valid mock succeeds
    result = await valid_mock_async_cli.execute_slot(
        "any_works", "divide", {"dividend": 15, "divisor": 6})
    assert result.success
    assert result.reason == ""
    assert type(result.reply) is dict
    assert result.reply["quotient"] == 2
    assert result.reply["remainder"] == 3
    # Checks that a correct async request to the invalid mock fails with an
    # error that the slot is not available
    result = await invalid_mock_async_cli.execute_slot(
        "none_works", "divide", {"dividend": 15, "divisor": 6})
    assert not result.success
    assert result.reason.startswith("none_works has no slot divide")
    assert result.reply is None

    # Checks that a correct sync request to the valid mock succeeds
    result = valid_mock_sync_cli.execute_slot(
        "any_works", "divide", {"dividend": 15, "divisor": 6})
    assert result.success
    assert result.reason == ""
    assert type(result.reply) is dict
    assert result.reply["quotient"] == 2
    assert result.reply["remainder"] == 3
    # Checks that a correct sync request to the invalid mock fails with an
    # error that the slot is not available
    result = invalid_mock_sync_cli.execute_slot(
        "none_works", "divide", {"dividend": 15, "divisor": 6})
    assert not result.success
    assert result.reason.startswith("none_works has no slot divide")
    assert result.reply is None


@pytest.mark.asyncio
async def test_injected_properties(web_proxy_mocks,
                                   valid_mock_async_cli,
                                   valid_mock_sync_cli,
                                   invalid_mock_async_cli,
                                   invalid_mock_sync_cli):
    # Checks that a sequence of correct async requests to the valid mock
    # succeeds
    result = await valid_mock_async_cli.add_injected_property("property_test",
                                                              "INT64")
    assert result.success
    assert result.reason == ""
    prop = await valid_mock_async_cli.get_injected_property("property_test")
    assert type(prop) is PropertyInfo
    result = await valid_mock_async_cli.set_injected_property(
        "property_test", PropertyInfo(value=28, timestamp=1720510279, tid=0))
    assert result.success
    assert result.reason == ""
    result = await valid_mock_async_cli.delete_injected_property(
        "property_test")
    assert result.success
    assert result.reason == ""

    # Checks that a sequence of correct async requests to the invalid mock
    # fails for every request.
    result = await invalid_mock_async_cli.add_injected_property(
        "property_test", "INT64")
    assert not result.success
    assert "property already existing" in result.reason
    with pytest.raises(RuntimeError,
                       match="Invalid response format"):
        await invalid_mock_async_cli.get_injected_property("property_test")
    result = await invalid_mock_async_cli.set_injected_property(
        "property_test", PropertyInfo(value=28, timestamp=1720510279, tid=0))
    assert not result.success
    assert "property not among the injected set" in result.reason
    result = await invalid_mock_async_cli.delete_injected_property(
        "property_test")
    assert not result.success
    assert "property not among the injected set" in result.reason

    # Checks that a sequence of correct sync requests to the valid mock
    # succeeds
    result = valid_mock_sync_cli.add_injected_property("property_test",
                                                       "INT64")
    assert result.success
    assert result.reason == ""
    prop = valid_mock_sync_cli.get_injected_property("property_test")
    assert type(prop) is PropertyInfo
    result = valid_mock_sync_cli.set_injected_property(
        "property_test", PropertyInfo(value=28, timestamp=1720510279, tid=0))
    assert result.success
    assert result.reason == ""
    result = valid_mock_sync_cli.delete_injected_property("property_test")
    assert result.success
    assert result.reason == ""

    # Checks that a sequence of correct sync requests to the invalid mock
    # fails for every request.
    result = invalid_mock_sync_cli.add_injected_property("property_test",
                                                         "INT64")
    assert not result.success
    assert "property already existing" in result.reason
    with pytest.raises(RuntimeError,
                       match="Invalid response format"):
        invalid_mock_sync_cli.get_injected_property("property_test")
    result = invalid_mock_sync_cli.set_injected_property(
        "property_test", PropertyInfo(value=28, timestamp=1720510279, tid=0))
    assert not result.success
    assert "property not among the injected set" in result.reason
    result = invalid_mock_sync_cli.delete_injected_property("property_test")
    assert not result.success
    assert "property not among the injected set" in result.reason
