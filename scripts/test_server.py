"""Quick test of auth + hardware listing against live server."""
import asyncio
import sys
sys.path.insert(0, "/home/nestor/milestone-linux-client")

from src.core.auth import AuthManager
from src.protocols.rest_api.client import RestClient
from src.protocols.rest_api.config import ConfigAPI


async def test():
    auth = AuthManager("https://milestone.putnamcountytn.gov", "test", "Test123!", "basic")
    rest = RestClient("https://milestone.putnamcountytn.gov", auth)

    token = auth.token
    print(f"Token OK: {token[:30]}...")

    config = ConfigAPI(rest)
    hw = await config.get_hardware()
    print(f"Hardware items: {len(hw)}")
    for item in hw[:5]:
        model = item.get("model", "N/A")
        name = item.get("displayName", "?")
        print(f"  {name}  [{model}]")

    await rest.close()


if __name__ == "__main__":
    asyncio.run(test())
    print("Done")
