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
    '  }'
    ' "client": {}'
    '}')  # "devices" and "servers" instead of singular forms; no "macro".

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

_app_valid = web.Application()
_app_valid.add_routes([web.get("/topology.json", _handle_topology)])

_app_invalid = web.Application()
_app_invalid.add_routes(
    ([web.get("/topology.json", _handle_topology_invalid)]))


async def run_valid_mock():
    await _run_mock(_app_valid, PORT_VALID_MOCK)


async def run_invalid_mock():
    await _run_mock(_app_invalid, PORT_INVALID_MOCK)


async def _run_mock(app, port):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
