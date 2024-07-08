from typing import Any, Dict

import requests

from .data.device_config import DeviceConfigInfo, PropertyValue
from .data.topology import DevicesInfo, TopologyInfo
from .data.web_proxy_responses import WriteResponse
from .message_format import (
    error_401_put, error_403_put, error_422_put, error_on_operation,
    invalid_response_format)


class SyncKaraboProxy:

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

    def get_topology(self) -> TopologyInfo:
        """Retrieves the topology of the topic containing the connected
        WebProxy."""
        resp = requests.get(f"{self.base_url}topology.json",
                            headers=self._headers)
        data = self._handle_get_response(resp, "gettting topology")
        try:
            topology_info = TopologyInfo(**data)
            return topology_info
        except TypeError as te:
            raise RuntimeError(invalid_response_format(str(te)))

    def get_devices(self) -> DevicesInfo:
        """Retrieves the devices in the topic containing the connected
        WebProxy."""
        resp = requests.get(f"{self.base_url}devices.json",
                            headers=self._headers)
        data = self._handle_get_response(resp, "gettting devices")
        try:
            devices_info = DevicesInfo(**data)
            return devices_info
        except TypeError as te:
            raise RuntimeError(invalid_response_format(str(te)))

    def get_device_configuration(self, device_id: str) -> DeviceConfigInfo:
        """Retrieves the configuration of a specified device."""
        resp = requests.get(
            f"{self.base_url}devices/{device_id}/config.json",
            headers=self._headers)
        data = self._handle_get_response(resp, "getting device configuration")
        try:
            device_config = dict(**data)
            return device_config
        except TypeError as te:
            raise RuntimeError(invalid_response_format(str(te)))

    def set_device_configuration(
            self, device_id: str,
            properties: Dict[str, PropertyValue]) -> WriteResponse:
        """Sets a given set of properties of a specified device (if the
        device is reconfigurable)"""
        resp = requests.put(
            f"{self.base_url}devices/{device_id}/config.json",
            json=properties, headers=self._headers)
        return self._handle_put_response(
            resp, "set configuration", device_id)

    def execute_slot(
        self, device_id: str, slot_name: str,
            slot_params: Dict[str, PropertyValue]) -> WriteResponse:
        """Executes a device slot. Supports both parameterless slots (commands)
        and slots with parameters. The results of the slot execution (if any)
        will be available as a dictionay in the field 'reply' of the response
        """
        resp = requests.put(
            f"{self.base_url}devices/{device_id}/slot/{slot_name}.json",
            json=slot_params, headers=self._headers)
        return self._handle_put_response(
            resp, f"execute slot {slot_name}", device_id)

    def _handle_get_response(self,
                             resp: requests.Response,
                             operation_name: str) -> Dict[str, Any]:

        if resp.status_code == 200:
            try:
                data = resp.json()
                return data
            except requests.exceptions.JSONDecodeError as e:
                raise RuntimeError(invalid_response_format(str(e)))
        else:
            # For some endpoints the WebProxy returns errors with a json
            # payload with a detail field. Retrieve any existing detail to
            # to provide better information to the user
            reason = resp.reason
            try:
                payload = resp.json()
                if "detail" in payload:
                    reason = f"{reason} - {payload['detail']}"
            finally:
                raise RuntimeError(error_on_operation(operation_name,
                                                      resp.status_code,
                                                      reason))

    def _handle_put_response(self,
                             resp: requests.Response,
                             operation_name: str,
                             device_id: str) -> WriteResponse:
        if resp.status_code == 200:
            try:
                data = resp.json()
                return WriteResponse(**data)
            except requests.exceptions.JSONDecodeError as e:
                return WriteResponse(success=False,
                                     reason=invalid_response_format(str(e)))
        elif resp.status_code == 401:
            return WriteResponse(
                success=False,
                reason=error_401_put(operation_name, device_id))
        elif resp.status_code == 403:
            return WriteResponse(
                success=False,
                reason=error_403_put(operation_name, device_id))
        elif resp.status_code == 422:
            return WriteResponse(
                success=False,
                reason=error_422_put(operation_name, device_id))
        else:
            return WriteResponse(
                success=False,
                reason=(error_on_operation(operation_name,
                                           resp.status_code,
                                           resp.reason)))


def main():
    client = SyncKaraboProxy("http://exflqr30450:8282")
    topology = client.get_topology()
    print(f"topology = {topology}")
    devices = client.get_devices()
    print(f"devices = {devices}")
    device_config = client.get_device_configuration("Karabo_GuiServer_0")
    print(f"device_config = {device_config}")
    client.set_access_token(
        # Token with no write permission - valid until 14.08.24
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjb3N0YXIiLCJ1c2VySW5m"
        "byI6eyJ1aWQiOjEwMjIsImxvZ2luIjoiY29zdGFyIiwibmFtZSI6IlJhdWwgQ29zdGEiL"
        "CJlbWFpbCI6InJhdWwuY29zdGFAeGZlbC5ldSJ9LCJwcm9wb3NhbE51bWJlciI6OTAwMz"
        "M0LCJwZXJtaXNzaW9ucyI6WzMsMV0sImV4cCI6MTcyMzYxMjAwN30.ZHK4GfWejLK1xpU"
        "73x_Il2aewoPm2yPiFPWvR-6wMsk")
    client.set_access_token(
        # Token with all permissions - - valid until 14.08.24
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjb3N0YXIiLCJ1c2VySW5m"
        "byI6eyJ1aWQiOjEwMjIsImxvZ2luIjoiY29zdGFyIiwibmFtZSI6IlJhdWwgQ29zdGEiL"
        "CJlbWFpbCI6InJhdWwuY29zdGFAeGZlbC5ldSJ9LCJwcm9wb3NhbE51bWJlciI6OTAwMz"
        "M0LCJwZXJtaXNzaW9ucyI6WzMsMSwyXSwiZXhwIjoxNzIzNjE0OTU5fQ.yv3XudlIGMbr"
        "lcvX6FdDsqJVBTx5cPwQgvr2I8uWovM")
    print()
    print("--- Set device configuration - flushInterval ---")
    print()
    result = client.set_device_configuration(
        "KARABO_DATALOGGERMANAGER_0", {"flushInterval": 85})
    print(result)
    print()
    print("--- Slot Execution: topologyCheck.slotForceCheck ---")
    print()
    result = client.execute_slot(
        "KARABO_DATALOGGERMANAGER_0", "topologyCheck.slotForceCheck", {})
    print(result)


if __name__ == "__main__":
    main()
