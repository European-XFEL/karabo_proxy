import json
from typing import Any, Dict

from aiohttp import ClientResponse, ClientSession

from .message_format import (
    error_401_put, error_403_put, error_422_put, error_on_operation,
    invalid_response_format)
from .schemas.device_config import DeviceConfigInfo, PropertyValue
from .schemas.topology import TopologyInfo
from .schemas.web_proxy_responses import WriteResponse


class AsyncKaraboProxy:

    def __init__(self, base_url: str):
        self.base_url = base_url
        self._headers = {
            "content-type": "application/json"}
        if not self.base_url.endswith("/"):
            # ensures the base_url ends with a path separator; this will be
            # assumed throughout the class
            self.base_url = f"{self.base_url}/"

    def set_access_token(self, access_token: str):
        self._headers["Authorization"] = f"Bearer {access_token}"

    async def get_topology(self) -> TopologyInfo:
        """Retrieves the topology of the topic containing the connected
        WebProxy."""
        async with ClientSession(headers=self._headers) as session:
            async with session.get(f"{self.base_url}topology.json") as resp:
                data = await self._handle_get_response(
                    resp, "getting topology")
                try:
                    topology_info = TopologyInfo(**data)
                    return topology_info
                except TypeError as te:
                    raise RuntimeError(invalid_response_format(str(te)))

    async def get_device_configuration(
            self, device_id: str) -> DeviceConfigInfo:
        """Retrieves the configuration of a specified device."""
        async with ClientSession(headers=self._headers) as session:
            async with session.get(
                    f"{self.base_url}devices/{device_id}/config.json") as resp:
                data = await self._handle_get_response(
                    resp, "getting device configuration")
                try:
                    device_config = dict(**data)
                    return device_config
                except TypeError as te:
                    raise RuntimeError(invalid_response_format(str(te)))

    async def set_device_configuration(
            self, device_id: str,
            properties: Dict[str, PropertyValue]) -> WriteResponse:
        """Sets a given set of properties of a specified device (if the
        device is reconfigurable)"""
        async with ClientSession(headers=self._headers) as session:
            async with session.put(
                f"{self.base_url}devices/{device_id}/config.json",
                    json=properties) as resp:
                return await self._handle_put_response(
                    resp, "set configuration", device_id)

    async def _handle_get_response(self,
                                   resp: ClientResponse,
                                   operation_name: str) -> Dict[str, Any]:
        if resp.status == 200:
            resp_body = await resp.text()
            try:
                data = json.loads(resp_body)
                return data
            except Exception as e:
                raise RuntimeError(invalid_response_format(str(e)))
        else:
            # For some endpoints the WebProxy returns errors with a json
            # payload with a detail field. Retrieve any existing detail to
            # to provide better information to the user
            reason = str(resp.reason)
            try:
                payload = json.loads(await resp.text())
                if "detail" in payload:
                    reason = f"{reason} - {payload['detail']}"
            finally:
                raise RuntimeError(error_on_operation(operation_name,
                                                      resp.status,
                                                      reason))

    async def _handle_put_response(self,
                                   resp: ClientResponse,
                                   operation_name: str,
                                   device_id: str) -> WriteResponse:
        if resp.status == 200:
            resp_body = await resp.text()
            try:
                data = json.loads(resp_body)
                return WriteResponse(**data)
            except Exception as e:
                return WriteResponse(success=False,
                                     reason=invalid_response_format(str(e)))
        elif resp.status == 401:
            return WriteResponse(
                success=False,
                reason=error_401_put(operation_name, device_id))
        elif resp.status == 403:
            return WriteResponse(
                success=False,
                reason=error_403_put(operation_name, device_id))
        elif resp.status == 422:
            return WriteResponse(
                success=False,
                reason=error_422_put(operation_name, device_id))
        else:
            return WriteResponse(
                success=False,
                reason=(error_on_operation(operation_name,
                                           resp.status,
                                           str(resp.reason))))


async def main():
    client = AsyncKaraboProxy("http://exflqr30450:8282")
    topology = await client.get_topology()
    print(f"topology = {topology}")
    device_config = await client.get_device_configuration("Karabo_GuiServer_0")
    print(f"device_config = {device_config}")
    client.set_access_token(
        # Token with no write permission - valid until 14.08.24
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjb3N0YXIiLCJ1c2VySW5m"
        "byI6eyJ1aWQiOjEwMjIsImxvZ2luIjoiY29zdGFyIiwibmFtZSI6IlJhdWwgQ29zdGEiL"
        "CJlbWFpbCI6InJhdWwuY29zdGFAeGZlbC5ldSJ9LCJwcm9wb3NhbE51bWJlciI6OTAwMz"
        "M0LCJwZXJtaXNzaW9ucyI6WzMsMV0sImV4cCI6MTcyMzYxMjAwN30.ZHK4GfWejLK1xpU"
        "73x_Il2aewoPm2yPiFPWvR-6wMsk")
    client.set_access_token(
        # Token with all permissions - valid until 14.08.24
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjb3N0YXIiLCJ1c2VySW5m"
        "byI6eyJ1aWQiOjEwMjIsImxvZ2luIjoiY29zdGFyIiwibmFtZSI6IlJhdWwgQ29zdGEiL"
        "CJlbWFpbCI6InJhdWwuY29zdGFAeGZlbC5ldSJ9LCJwcm9wb3NhbE51bWJlciI6OTAwMz"
        "M0LCJwZXJtaXNzaW9ucyI6WzMsMSwyXSwiZXhwIjoxNzIzNjE0OTU5fQ.yv3XudlIGMbr"
        "lcvX6FdDsqJVBTx5cPwQgvr2I8uWovM")
    result = await client.set_device_configuration(
        "KARABO_DATALOGGERMANAGER_0", {"flushInterval": 55})
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
