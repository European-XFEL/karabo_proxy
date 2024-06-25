#############################################################################
# Author: degon
#
# Created on June 25, 2024, 04:34 PM
# from template 'minimal middlelayer' of Karabo 2.20.1.dev26+gb8be1dc2c.d20240620
#
# This file is intended to be used together with Karabo:
#
# http://www.karabo.eu
#
# IF YOU REQUIRE ANY LICENSING AND COPYRIGHT TERMS, PLEASE ADD THEM HERE.
# Karabo itself is licensed under the terms of the MPL 2.0 license.
#############################################################################
import pytest

from karabo.middlelayer.testing import AsyncDeviceContext, event_loop

from ..Karabo-proxy import Karabo-proxy


_DEVICE_ID = "TestKarabo-proxy"
_DEVICE_CONFIG = {
    "_deviceId_": _DEVICE_ID,
}


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_device(event_loop: event_loop):
    device = Karabo-proxy(_DEVICE_CONFIG)
    async with AsyncDeviceContext(device=device) as ctx:
        assert ctx.instances["device"] is device
        assert ctx.instances["device"].deviceId == _DEVICE_ID
