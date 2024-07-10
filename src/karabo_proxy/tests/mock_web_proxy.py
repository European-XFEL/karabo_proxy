import argparse

from aiohttp import web

# region Mocks Responses

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

DEVICES_RESPONSE_VALID = (
    '{'
    '  "devices": {'
    '    "A_SIMPLE_DEVICE": {"__deviceId__": "A_SIMPLE_DEVICE"}'
    '  }'
    '}')

DEVICES_RESPONSE_INVALID = (
    '{'
    '  "device": {'
    '    "A_SIMPLE_DEVICE": {"__deviceId__": "A_SIMPLE_DEVICE"}'
    '  }'
    '}')  # "device" instead of "devices"

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

DEVICE_SET_CONFIGURATION_INVALID = (
    '{'
    '  "success": false, '
    '  "reason": "Lacking valid access_token with permissions ..."'
    '}')

DEVICE_GET_SCHEMA_VALID = (
    '{'
    '  "_deviceId_": { '
    '     "displayedName": "_DeviceID_", '
    '     "description": "Do not set this property.", '
    '     "requiredAccessLevel": "ADMIN" '
    '  }, '
    '  "heartbeatInterval" :{ '
    '     "displayedName": "Heartbeat interval", '
    '     "description": "Interval in seconds between device heartbeats", '
    '     "requiredAccessLevel": "ADMIN" '
    '  } '
    '}')

DEVICE_GET_SCHEMA_INVALID = (
    '{'
    '  "detail": "Device not online or not alive"'
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

ADD_INJECTED_PROPERTY_INVALID = (
    '{'
    '  "success": false, '
    '  "reason": "property already existing"'
    '}')

GET_PROPERTY_VALID = (
    '{'
    '  "value": 28, '
    '  "timestamp": 1720508183, '
    '  "tid": 0 '
    '}')

GET_INJECTED_PROPERTY_INVALID = (
    '{'
    '  "value": 28, '
    '  "timestamp": 1720508183 '
    '}')  # missing tid

INVALID_MODIFY_INJECTED_PROPERTY = (
    '{'
    '  "success": false, '
    '  "reason": "property not among the injected set"'
    '}')

VALID_MODIFY_RESPONSE = (
    '{'
    '  "success": true, '
    '  "reason": ""'
    '}')

# endregion

# Port listened by the mock that returns valid responses
PORT_VALID_MOCK = 8383
# Port listened by the mock that returns invalid responses
PORT_INVALID_MOCK = 8484

# region Request Handlers


async def _handle_topology(request):
    return web.Response(
        content_type="application/json",
        text=TOPOLOGY_RESPONSE_VALID)


async def _handle_topology_invalid(request):
    return web.Response(
        content_type="application/json",
        text=TOPOLOGY_RESPONSE_INVALID)


async def _handle_devices(request):
    return web.Response(
        content_type="application/json",
        text=DEVICES_RESPONSE_VALID)


async def _handle_devices_invalid(request):
    return web.Response(
        content_type="application/json",
        text=DEVICES_RESPONSE_INVALID)


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
        text=VALID_MODIFY_RESPONSE)


async def _handle_set_device_configuration_invalid(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_SET_CONFIGURATION_INVALID)


async def _handle_get_config_path(request):
    return web.Response(
        content_type="application/json",
        text=GET_PROPERTY_VALID)


async def _handle_get_config_path_invalid(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_GET_CONFIGURATION_INVALID)


async def _handle_set_config_path(request):
    return web.Response(
        content_type="application/json",
        text=VALID_MODIFY_RESPONSE)


async def _handle_set_config_path_invalid(request):
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


async def _handle_get_device_schema(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_GET_SCHEMA_VALID)


async def _handle_get_device_schema_invalid(request):
    return web.Response(
        content_type="application/json",
        text=DEVICE_GET_SCHEMA_INVALID,
        status=500)


async def _handle_add_injected_property(request):
    return web.Response(
        content_type="application/json",
        text=VALID_MODIFY_RESPONSE)


async def _handle_add_injected_property_invalid(request):
    return web.Response(
        content_type="application/json",
        text=ADD_INJECTED_PROPERTY_INVALID)


async def _handle_get_injected_property(request):
    return web.Response(
        content_type="application/json",
        text=GET_PROPERTY_VALID)


async def _handle_get_injected_property_invalid(request):
    return web.Response(
        content_type="application/json",
        text=GET_INJECTED_PROPERTY_INVALID)


async def _handle_set_injected_property(request):
    return web.Response(
        content_type="application/json",
        text=VALID_MODIFY_RESPONSE)


async def _handle_set_injected_property_invalid(request):
    return web.Response(
        content_type="application/json",
        text=INVALID_MODIFY_INJECTED_PROPERTY)


async def _handle_delete_injected_property(request):
    return web.Response(
        content_type="application/json",
        text=VALID_MODIFY_RESPONSE)


async def _handle_delete_injected_property_invalid(request):
    return web.Response(
        content_type="application/json",
        text=INVALID_MODIFY_INJECTED_PROPERTY)


# endregion

_app_valid = web.Application()
_app_valid.add_routes([
    web.get("/topology.json", _handle_topology),
    web.get("/devices.json", _handle_devices),
    # Note: Due to the way that aiohttp.web.WebApplication matches routes,
    #       the route for individual property paths must be declared before
    #       the route for the whole device configuration. If that's not the
    #       case, the route for the whole device configuration will be matched
    #       for requests for individual property paths.
    web.get("/devices/{device_id}.{propertyName}/config.json",
            _handle_get_config_path),
    web.put("/devices/{device_id}.{propertyName}/config.json",
            _handle_set_config_path),
    web.get("/devices/{device_id}/config.json",
            _handle_get_device_configuration),
    web.put("/devices/{device_id}/config.json",
            _handle_set_device_configuration),
    web.get("/devices/{device_id}/schema.json",
            _handle_get_device_schema),
    web.put("/devices/{device_id}/slot/{slot_name}.json",
            _handle_execute_slot),
    web.post("/property/property_test/config.json",
             _handle_add_injected_property),
    web.get("/property/property_test/config.json",
            _handle_get_injected_property),
    web.put("/property/property_test/config.json",
            _handle_set_injected_property),
    web.delete("/property/property_test/config.json",
               _handle_delete_injected_property),
])


_app_invalid = web.Application()
_app_invalid.add_routes([
    web.get("/topology.json", _handle_topology_invalid),
    web.get("/devices.json", _handle_devices_invalid),
    # Note: Due to the way that aiohttp.web.WebApplication matches routes,
    #       the route for individual property paths must be declared before
    #       the route for the whole device configuration. If that's not the
    #       case, the route for the whole device configuration will be matched
    #       for requests for individual property paths.
    web.get("/devices/{device_id}.{propertyName}/config.json",
            _handle_get_config_path_invalid),
    web.put("/devices/{device_id}.{propertyName}/config.json",
            _handle_set_config_path_invalid),
    web.get("/devices/{device_id}/config.json",
            _handle_get_device_configuration_invalid),
    web.put("/devices/{device_id}/config.json",
            _handle_set_device_configuration_invalid),
    web.get("/devices/{device_id}/schema.json",
            _handle_get_device_schema_invalid),
    web.put("/devices/{device_id}/slot/{slot_name}.json",
            _handle_execute_slot_invalid),
    web.post("/property/property_test/config.json",
             _handle_add_injected_property_invalid),
    web.get("/property/property_test/config.json",
            _handle_get_injected_property_invalid),
    web.put("/property/property_test/config.json",
            _handle_set_injected_property_invalid),
    web.delete("/property/property_test/config.json",
               _handle_delete_injected_property_invalid),
])

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
