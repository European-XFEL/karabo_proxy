import requests

from .schemas.web_proxy_responses import TopologyInfo


class SyncKaraboProxy:

    def __init__(self, base_url: str):
        self.base_url = base_url
        if not self.base_url.endswith("/"):
            # ensures the base_url ends with a path separator; this will be
            # assumed throughout the class
            self.base_url = f"{self.base_url}/"

    def get_topology(self) -> TopologyInfo:
        """Retrieves the topology of the topic containing the connected
        WebProxy."""
        resp = requests.get(f"{self.base_url}topology.json")
        if resp.status_code == 200:
            try:
                data = resp.json()
                return TopologyInfo(**data)
            except requests.exceptions.JSONDecodeError as e:
                raise RuntimeError(f"Invalid response format: {e}")
        else:
            raise RuntimeError(
                f"Error retrieving topology: {resp.reason}"
                f"({resp.status_code})")


def main():
    client = SyncKaraboProxy("http://exflqr30450:8282")
    topology = client.get_topology()
    print(f"topology = {topology}")


if __name__ == "__main__":
    main()
