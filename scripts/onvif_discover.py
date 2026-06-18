#!/usr/bin/env python3
"""
Standalone ONVIF camera discovery script.

Usage: python onvif_discover.py [--timeout 5]
"""
import asyncio
import sys
from src.protocols.onvif.discovery import discover_onvif_devices, get_device_info


async def main():
    timeout = 5
    if len(sys.argv) > 1 and sys.argv[1] == "--timeout":
        timeout = int(sys.argv[2])

    print(f"Scanning for ONVIF devices (timeout={timeout}s)...")
    devices = await discover_onvif_devices(timeout)

    if not devices:
        print("No ONVIF devices found.")
        return

    print(f"\nFound {len(devices)} device(s):\n")
    for i, d in enumerate(devices):
        print(f"  [{i+1}] {d.address}")
        print(f"       XAddrs: {d.xaddrs}")
        print(f"       Scopes: {d.scopes[:100]}..." if len(d.scopes) > 100 else f"       Scopes: {d.scopes}")
        info = await get_device_info(d.xaddrs)
        if "manufacturer" in info:
            print(f"       Manufacturer: {info.get('manufacturer', 'N/A')}")
            print(f"       Model: {info.get('model', 'N/A')}")
            print(f"       Firmware: {info.get('firmware', 'N/A')}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
