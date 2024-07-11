# Karabo-Proxy

## Overview

The Karabo WebProxy device exposes a web API that allows any HTTP client to
interact with devices in its [Karabo](http://karabo.eu) topic.

This project, **Karabo-Proxy**, provides a convenience Python 3 client library for
interacting with an instance of the Karabo WebProxy device in a (mostly)
HTTP-agnostic way.

Karabo-Proxy offers two client variants, **SyncKaraboProxy** and
**AsyncKaraboProxy**, with a common interface. The first is a synchronous
(blocking) client and the second is an asynchronous (`asyncio`-friendly) client.

Examples of use of both clients in some common scenarios are shown below. For full
details please look at the docstrings available in the library.

## Installation

### From a local clone of the project

```
git clone https://github.com/European-XFEL/karabo_proxy.git
cd karabo_proxy
pip install .
```

### From pypi.org

```
pip install karabo_proxy
````

## How to Use

### Connect to a WebProxy instance

```
from karabo_proxy import SyncKaraboProxy

client = SyncKaraboProxy("http://web_proxy_host:8282")
```

```
from karabo_proxy import AsyncKaraboProxy

async_client = AsyncKaraboProxy("http://web_proxy_host:8282")
```

### Retrieve the Topology of the Karabo Topic

The topology is returned as an object of type `karabo_proxy.data.topology.TopologyInfo`.

```
topology = client.get_topology()
```

```
topology = await async_client.get_topology()
```

### Get the Configuration of a Device

The device configuration is returned as a dictionary where the identifiers of the device
properties are the keys and the values are of type `karabo_proxy.data.device_config.PropertyInfo` (property value with timing information).

```
config = client.get_device_configuration("DEVICE_ID")
```

```
config = await async_client.get_device_configuration("DEVICE_ID")
```

### Configure a Device

This operation is only allowed on devices that are in the list of `reconfigurableDevices`
of the connected WebProxy. The properties being set should be provided as a dictionary
where the key is the property identifier and the value is the value to be set for the property.

```
result = client.set_device_configuration("DEVICE_ID",
                                         "{"prop_1": 3.14159,
                                         "prop_2": "activating ..." })
```

```
result = await async_client.set_device_configuration("DEVICE_ID",
                                                     "{"prop_1": 3.14159,
                                                     "prop_2": "activating ..." })
```

`result` will be an object with two attributes: `success` (bool) and `reason` (str).
`reason` is empty for successful operations. Otherwise (`success == False`), it
contains an error message detailing what went wrong.

### Execute a Device Slot

Slot execution requires the specified device to be in the list of `reconfigurableDevices`
of the connected WebProxy. Its return value has the same type and semantics of the
return value of the `set_device_configuration` operation.

```
result = client.execute_slot("DEVICE_ID",
                             "slot_start", {"param1": "NOW", "param2": 30})
```

```
result = await async_client.execute_slot("DEVICE_ID",
                                         "slot_start",
                                         {"param1": "NOW", "param2": 30})
```

The slot parameters, if any, should be passed as a dictionary with the parameter
name as the key and the value as the value.

## Contact

For questions, please contact opensource@xfel.eu.

## License and Contributing

This software is released by the European XFEL GmbH as is and without any warranty under the GPLv3 license. If you have questions on contributing to the project, please get in touch at opensource@xfel.eu.
