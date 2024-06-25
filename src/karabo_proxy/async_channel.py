#############################################################################
# Copyright (C) European XFEL GmbH Schenefeld. All rights reserved.
#############################################################################

import logging
import socket
from asyncio import (
    CancelledError, IncompleteReadError, Lock, get_event_loop,
    iscoroutinefunction, open_connection, shield, sleep)
from contextlib import closing
from functools import wraps
from struct import calcsize, pack, unpack

from karabo.native import Hash, decodeBinary, encodeBinary

REBOUND_SLEEP = 2


class Channel:
    """This class is responsible for reading and writing Hashes to TCP

    It is the low-level implementation of the pipeline protocol."""
    sizeCode = "<I"

    def __init__(self, reader, writer, channelName=None):
        self.reader = reader
        self.writer = writer
        self.drain_lock = Lock()
        self.channelName = channelName

    async def readBytes(self):
        buf = (await self.reader.readexactly(calcsize(self.sizeCode)))
        size, = unpack(self.sizeCode, buf)
        return (await self.reader.readexactly(size))

    async def readHash(self):
        r = await self.readBytes()
        return decodeBinary(r)

    def writeHash(self, hsh):
        data = encodeBinary(hsh)
        self.writeSize(len(data))
        self.writer.write(data)

    def writeSize(self, size):
        self.writer.write(pack(self.sizeCode, size))

    def close(self):
        self.writer.close()


def ensure_coroutine(coro):
    """Ensure that a function `coro` is a coroutine to play well
    in our eventloops"""
    if iscoroutinefunction(coro):
        return coro

    def create_coroutine(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    return create_coroutine(coro)


class AsyncChannelClient:
    """The Async Channel Client to connect to a Karabo Output channel

    The data is received as a `Karabo.Hash`

    Use different handlers for patching:

    - AsyncChannelClient.connect_handler(channel_name)
      This handler is called when we are connected

    - AsyncChannelClient.close_handler(channel_name)
      This handler is called when the channel was closed

    - AsyncChannelClient.handler(data, meta)
      This handler is called when data arrives

    - AsyncChannelClient.end_of_stream_handler(channel_name)
      This handler is called when the end of steam signal is received
    """

    name = None

    def __init__(self, host="localhost", port=0, reconnect=True,
                 level=logging.INFO):
        self.onSlowness = "drop"
        self.dataDistribution = "copy"
        self.delayOnInput = 0
        self.handler_lock = Lock()
        self.host = host
        self.port = int(port)
        self.task = None
        self.initialized = False
        self.name = f"AsyncChannelClient<{host, port}>"
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(level)
        self.reconnect = reconnect

    def connect(self):
        loop = get_event_loop()
        self.task = loop.create_task(self.start_channel(self.host, self.port))

    def cancel(self):
        if self.task is not None and not self.task.done():
            self.task.cancel()

    stop = cancel

    async def wait_closed(self):
        if self.task is not None:
            await self.task

    async def handler(self, data, meta):
        self.logger.info(f"Received data for meta {meta}")

    async def connect_handler(self, output):
        self.logger.info("Connect handler called by {}!".format(output))

    async def close_handler(self, output):
        self.logger.info("Close handler called by {}!".format(output))

    async def end_of_stream_handler(self, output):
        self.logger.info("EndOfStream handler called by {}!".format(output))

    async def call_handler(self, func, *args):
        """Call a network input handler under mutex and error protection"""
        async with self.handler_lock:
            try:
                await ensure_coroutine(func)(*args)
            except BaseException:
                pass

    async def start_channel(self, hostname, port):
        """Connect to the output channel with Id 'output' """
        self.logger.info(f"Try to connect to {hostname}:{port} ...")
        self.initialized = True
        try:
            output = self.name
            reader, writer = await open_connection(hostname, int(port))
            channel = Channel(reader, writer, channelName=output)
            with closing(channel):
                await shield(self.call_handler(self.connect_handler, output))
                cmd = Hash("reason", "hello",
                           "instanceId", self.name,
                           "memoryLocation", "remote",
                           "dataDistribution", self.dataDistribution,
                           "onSlowness", self.onSlowness,
                           "maxQueueLength", 2)
                channel.writeHash(cmd)
                while (await self.processChunk(channel, None, self.name)):
                    await sleep(self.delayOnInput)
                    self.logger.debug(f"Requesting new data for {output}")
                else:
                    await shield(self.call_handler(self.close_handler, output))
                    if self.reconnect:
                        self.logger.info(
                            f"Trying to reconnect to {hostname}:{port}")
                        await sleep(REBOUND_SLEEP)
                        await self.start_channel(hostname, port)
                    else:
                        self.logger.info(f"Exiting Channel for {output}")
        except CancelledError:
            self.logger.error("AsyncKaraboChannel got cancelled.")
        except Exception:
            await shield(self.call_handler(self.close_handler, output))
            if self.reconnect:
                self.logger.error(
                    f"Trying to reconnect to {hostname}:{port}")
                await sleep(REBOUND_SLEEP)
                await self.start_channel(hostname, port)
            else:
                self.logger.info(f"Exiting Channel for {output}")

    async def processChunk(self, channel, cls, output_id=""):
        try:
            header = await channel.readHash()
        except IncompleteReadError as e:
            if e.partial:
                raise
            else:
                self.logger.info(f"Stream finished for {output_id}")
                return False
        data = await channel.readBytes()
        cmd = Hash("reason", "update",
                   "instanceId", output_id)
        channel.writeHash(cmd)
        if "endOfStream" in header:
            await shield(self.call_handler(
                self.end_of_stream_handler, output_id))
            return True
        pos = 0
        for length, meta_hash in zip(header["byteSizes"],
                                     header["sourceInfo"]):
            chunk = decodeBinary(data[pos:pos + length])
            await shield(self.call_handler(self.handler, chunk, meta_hash))
            pos += length
        return True


def main():
    # Put basic logging configuration first
    # XXX: Implement argparse for host and port
    logging.basicConfig()

    print("Starting the Karabo Channel Client")
    loop = get_event_loop()
    hostname = socket.gethostname()
    client = AsyncChannelClient(host=hostname, port=38198,
                                reconnect=True,
                                level=logging.DEBUG)
    client.connect()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        client.cancel()
        loop.run_until_complete(client.wait_closed())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
