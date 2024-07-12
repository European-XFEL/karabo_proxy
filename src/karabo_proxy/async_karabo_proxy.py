import json
from dataclasses import asdict
from typing import Any, Dict, Optional

from aiohttp import ClientResponse, ClientSession

from .data.device_config import DeviceConfigInfo, PropertyInfo, PropertyValue
from .data.topology import DevicesInfo, TopologyInfo
from .data.web_proxy_responses import WriteResponse
from .message_format import (
    error_401_put, error_403_put, error_422_put, error_on_operation,
    invalid_response_format)


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

    async def get_devices(self) -> DevicesInfo:
        """Retrieves the devices in the topic containing the connected
        WebProxy."""
        async with ClientSession(headers=self._headers) as session:
            async with session.get(f"{self.base_url}devices.json") as resp:
                data = await self._handle_get_response(
                    resp, "getting devices")
                try:
                    devices_info = DevicesInfo(**data)
                    return devices_info
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
                return await self._handle_write_response(
                    resp, "set configuration", device_id)

    async def get_device_config_path(
            self, device_id: str, property_name: str) -> PropertyInfo:
        """Retrieves the value and time attributes of a specified device
        property."""
        async with ClientSession(headers=self._headers) as session:
            async with session.get(
                    f"{self.base_url}devices/"
                    f"{device_id}.{property_name}/config.json") as resp:
                data = await self._handle_get_response(
                    resp, "getting device property")
                try:
                    property_info = PropertyInfo(**data)
                    return property_info
                except TypeError as te:
                    raise RuntimeError(invalid_response_format(str(te)))

    async def set_device_config_path(
            self, device_id: str, property_name: str,
            property_value: PropertyValue) -> WriteResponse:
        """Sets a property of a specified device (if the device is
        reconfigurable)."""
        async with ClientSession(headers=self._headers) as session:
            async with session.put(
                f"{self.base_url}devices/"
                f"{device_id}.{property_name}/config.json",
                    json=property_value) as resp:
                return await self._handle_write_response(
                    resp, "set property", f"{device_id}.{property_name}")

    async def get_device_schema(
            self, device_id: str) -> Dict[str, Dict[str, Any]]:
        """Retrieves the schema of a specified device.

        Parameters:
        device_id(str):the device whose schema should be retrieved

        Returns:
        A dictionary whose keys are the properties of the device and the
        values are dictionaries with the names of the attributes of the
        property as keys and the values of the attributes as values.

        e.g:
        {'deviceId': {
             'displayedName': 'DeviceID',
             'description': 'The device instance ID',
             'assignment': 'OPTIONAL',
             ...
            },
         'heartbeatInterval': {
            'displayedName': 'Heartbeat interval',
            ...
            }
         ...
        }
        """
        async with ClientSession(headers=self._headers) as session:
            async with session.get(
                    f"{self.base_url}devices/{device_id}/schema.json") as resp:
                data = await self._handle_get_response(
                    resp, "getting device schema")
                try:
                    schema = dict(**data)
                    return schema
                except TypeError as te:
                    raise RuntimeError(invalid_response_format(str(te)))

    async def execute_slot(
            self, device_id: str, slot_name: str,
            slot_params: Optional[
                Dict[str, PropertyValue]] = None) -> WriteResponse:
        """Executes a device slot. Supports both parameterless slots (commands)
        and slots with parameters. The results of the slot execution (if any)
        will be available as a dictionay in the field 'reply' of the response
        """
        async with ClientSession(headers=self._headers) as session:
            async with session.put(
                f"{self.base_url}devices/{device_id}/slot/{slot_name}.json",
                    json=slot_params) as resp:
                return await self._handle_write_response(
                    resp, f"execute slot {slot_name}", device_id)

# region Injected Property endpoints

    async def add_injected_property(
            self, property_name: str, property_type: str) -> WriteResponse:
        """Adds a property to the set of injected properties of the WebProxy
        instance.

        Parameters:
        property_name(str): the name of the property to be injected - cannot
        contain any dot ('.') as the dot is the separator character for
        Karabo's Hash paths and may introduce inconsistencies.

        property_type(str): the type of the property to add. Allowed values are
        "STRING", "INT64", "DOUBLE", "VECTOR_STRING", "VECTOR_INT64", and
        "VECTOR_DOUBLE".

        Returns:
        WriteResponse: was the operation successful? If not, what was the
        reason for the failure?

        Raises:
        RuntimeError if the property name is invalid, the property type is not
        supported or the user is not authorized for the operation.
        """
        async with ClientSession(headers=self._headers) as session:
            async with session.post(
                    f"{self.base_url}property/"
                    f"{property_name}/config.json",
                    json={"valueType": property_type}) as resp:
                return await self._handle_write_response(
                    resp, "inject property", property_name)

    async def get_injected_property(
            self, property_name: str) -> PropertyInfo:
        """Retrieves the value of a specified injected property.

        Parameters:
        property_name(str): the name of the injected property.

        Returns:
        PropertyInfo: data class with value, timestamp and tid (train_id) of
        the property

        Raises:
        RuntimeError if property_name is not a known injected property.
        """
        async with ClientSession(headers=self._headers) as session:
            async with session.get(
                    f"{self.base_url}property/"
                    f"{property_name}/config.json") as resp:
                data = await self._handle_get_response(
                    resp, "getting injected property value")
                try:
                    injected_property = PropertyInfo(**data)
                    return injected_property
                except TypeError as te:
                    raise RuntimeError(invalid_response_format(str(te)))

    async def set_injected_property(
            self, property_name: str, property: PropertyInfo) -> WriteResponse:
        """Sets the value and timing attributes of a property previously
        injected into the WebProxy instance.

        Parameters:
        property_name(str): the name of the injected property.

        property(PropertyInfo): the value and timing attributes to be set for
        the injected property

        Returns:
        WriteResponse: was the operation successful? If not, what was the
        reason for the failure?

        Raises:
        RuntimeError if the injected property was not found, the property type
        is not supported or the user is not authorized for the operation.
        """
        async with ClientSession(headers=self._headers) as session:
            async with session.put(
                    f"{self.base_url}property/"
                    f"{property_name}/config.json",
                    json=asdict(property)) as resp:
                return await self._handle_write_response(
                    resp, "set injected property value", property_name)

    async def delete_injected_property(self,
                                       property_name: str) -> WriteResponse:
        """Removes the specified property from the set of properties injected
        into the WebProxy instance.

        Parameters:
        property_name(str): the name of the injected property.

        Returns:
        WriteResponse: was the operation successful? If not, what was the
        reason for the failure?

        Raises:
        RuntimeError if the injected property was not found, or the user is
        not authorized for the operation.
        """
        async with ClientSession(headers=self._headers) as session:
            async with session.delete(
                    f"{self.base_url}property/"
                    f"{property_name}/config.json") as resp:
                return await self._handle_write_response(
                    resp, "delete injected property", property_name)

# endregion

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

    async def _handle_write_response(self,
                                     resp: ClientResponse,
                                     operation_name: str,
                                     operand_id: str) -> WriteResponse:
        """Handles the response of a write operation - POST, PUT or DELETE
        HTTP verbs"""
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
                reason=error_401_put(operation_name, operand_id))
        elif resp.status == 403:
            return WriteResponse(
                success=False,
                reason=error_403_put(operation_name, operand_id))
        elif resp.status == 422:
            return WriteResponse(
                success=False,
                reason=error_422_put(operation_name, operand_id))
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
    devices = await client.get_devices()
    print(f"devices = {devices}")
    print()
    print("--- Get device schema ---")
    print()
    schema = await client.get_device_schema("Karabo_GuiServer_0")
    print(f"schema = {schema}")
    print()
    print("--- Get device configuration ---")
    print()
    device_config = await client.get_device_configuration("Karabo_GuiServer_0")
    print(f"device_config = {device_config}")
    print()
    print("--- Get device property (config path) - flushInterval ---")
    print()
    prop = await client.get_device_config_path("KARABO_DATALOGGERMANAGER_0",
                                               "flushInterval")
    print(prop)
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
    print()
    print("--- Set device configuration - flushInterval ---")
    print()
    result = await client.set_device_configuration(
        "KARABO_DATALOGGERMANAGER_0", {"flushInterval": 55})
    print(result)
    print()
    result = await client.set_device_config_path("KARABO_DATALOGGERMANAGER_0",
                                                 "flushInterval", 65)
    print(result)
    print()
    print("--- Slot Execution: topologyCheck.slotForceCheck ---")
    print()
    result = await client.execute_slot(
        "KARABO_DATALOGGERMANAGER_0", "topologyCheck.slotForceCheck")
    print(result)
    print()
    print("--- Full property injection cycle: flushInterval ---")
    print()
    result = await client.add_injected_property("flushInterval", "INT64")
    print(f"add_injected_property result: {result}")
    result = await client.set_injected_property(
        "flushInterval",
        PropertyInfo(value=80, timestamp=100.0, tid=0))
    print(f"set_injected_property result: {result}")
    property = await client.get_injected_property("flushInterval")
    print(f"get_injected_property: {property}")
    result = await client.delete_injected_property("flushInterval")
    print(result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
