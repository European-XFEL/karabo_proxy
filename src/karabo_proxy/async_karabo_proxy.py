import json

from aiohttp import ClientSession

from .schemas.web_proxy_responses import TopologyInfo


class AsyncKaraboProxy:

    def __init__(self, base_url: str):
        self.base_url = base_url
        if not self.base_url.endswith("/"):
            # ensures the base_url ends with a path separator; this will be
            # assumed throughout the class
            self.base_url = f"{self.base_url}/"

    async def get_topology(self) -> TopologyInfo:
        """Retrieves the topology of the topic containing the connected
        WebProxy."""
        async with ClientSession() as session:
            async with session.get(f"{self.base_url}topology.json") as resp:
                if resp.status == 200:
                    resp_body = await resp.text()
                    try:
                        data = json.loads(resp_body)
                        return TopologyInfo(**data)
                    except Exception as e:
                        raise RuntimeError(f"Invalid response format: {e}")
                else:
                    raise RuntimeError(
                        f"Error retrieving topology: {resp.reason}"
                        f"({resp.status})")


async def main():
    client = AsyncKaraboProxy("http://exflqr30450:8282")
    topology = await client.get_topology()
    print(f"topology = {topology}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
