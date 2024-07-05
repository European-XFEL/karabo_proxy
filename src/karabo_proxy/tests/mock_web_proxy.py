import argparse

from aiohttp import web

TOPOLOGY_RESPONSE_VALID = (
    '{'
    '  "device": {'
    '    "A_SIMPLE_DEVICE": {"__deviceId__": "A_SIMPLE_DEVICE"}'
    '  }, '
    '  "server": {'
    '    "A_SIMPLE_SERVER": {"__serverId__": "A_SIMPLE_SERVER"}'
    '  }, '
    ' "client": {}, "macro": {}'
    '}')

TOPOLOGY_RESPONSE_INVALID = (
    '{'
    '  "devices": {'
    '    "A_SIMPLE_DEVICE": {"__deviceId__": "A_SIMPLE_DEVICE"}'
    '  }, '
    '  "servers": {'
    '    "A_SIMPLE_SERVER": {"__serverId__": "A_SIMPLE_SERVER"}'
    '  },'
    ' "client": {}'
    '}')  # "devices" and "servers" instead of singular forms; no "macro".

DEVICE_GET_CONFIGURATION_VALID = (
    '{'
    '  "_deviceId_":{"value":"Karabo_GuiServer_0", '
    '                "timestamp": 1719838221.5852, "tid": 0},'
    '  "deviceId":{"value":"Karabo_GuiServer_0", '
    '              "timestamp": 1719838221.5852, "tid": 0}'
    '}')

# the WebProxy returns a status code 500 with the following payload
# for an attempt to get the configuration of a device not in the topology
DEVICE_GET_CONFIGURATION_INVALID = (
    '{'
    '  "detail": "Device Karabo_GuiServer_XYZ not online or not alive"'
    '}')

DEVICE_SET_CONFIGURATION_VALID = (
    '{'
    '  "success": true, '
    '  "reason": ""'
    '}')

DEVICE_SET_CONFIGURATION_INVALID = (
    '{'
    '  "success": false, '
    '  "reason": "Lacking valid access_token with permissions ..."'
    '}')

DEVICE_EXECUTE_SLOT_VALID = (
    '{'
    '  "success": true, '
    '  "reason": "", '
    '  "reply": {'
    '            "quotient": 2, '
    '            "remainder": 3 '
    '           } '
    '}')

DEVICE_EXECUTE_SLOT_INVALID = (
    '{'
    '  "success": false, '
    '  "reason": "none_works has no slot divide"'
    '}')


# Port listened by the mock that returns valid responses
PORT_VALID_MOCK = 8383
# Port listened by the mock that returns invalid responses
PORT_INVALID_MOCK = 8484


async def _handle_topology(request):
    return web.Response(
        content_type="application/json",
        text=TOPOLOGY_RESPONSE_VALID)


async def _handle_topology_invalid(request):
    return web.Response(
        content_type="application/json",
        text=TOPOLOGY_RESPONSE_INVALID)


async def _handle_get_device_configuration(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_GET_CONFIGURATION_VALID)


async def _handle_get_device_configuration_invalid(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_GET_CONFIGURATION_INVALID,
        status=500,
        reason="Internal Server Error")


async def _handle_set_device_configuration(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_SET_CONFIGURATION_VALID)


async def _handle_set_device_configuration_invalid(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_SET_CONFIGURATION_INVALID)


async def _handle_execute_slot(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_EXECUTE_SLOT_VALID)


async def _handle_execute_slot_invalid(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_EXECUTE_SLOT_INVALID)


_app_valid = web.Application()
_app_valid.add_routes([
    web.get("/topology.json", _handle_topology),
    web.get("/devices/{device_id}/config.json",
            _handle_get_device_configuration),
    web.put("/devices/{device_id}/config.json",
            _handle_set_device_configuration),
    web.put("/devices/{device_id}/slot/{slot_name}.json",
            _handle_execute_slot)])

_app_invalid = web.Application()
_app_invalid.add_routes([
    web.get("/topology.json", _handle_topology_invalid),
    web.get("/devices/{device_id}/config.json",
            _handle_get_device_configuration_invalid),
    web.put("/devices/{device_id}/config.json",
            _handle_set_device_configuration_invalid),
    web.put("/devices/{device_id}/slot/{slot_name}.json",
            _handle_execute_slot_invalid)])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="mock_web_proxy",
        description="WebProxy Mocker")
    parser.add_argument("--invalid", action="store_true")
    args = parser.parse_args()
    if args.invalid:
        print("Launching mock in invalid mode...")
        web.run_app(_app_invalid, port=PORT_INVALID_MOCK)
    else:
        print("Launching mock in valid mode...")
        web.run_app(_app_valid, port=PORT_VALID_MOCK)
