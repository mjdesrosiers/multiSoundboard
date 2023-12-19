import asyncio, evdev
import os

from evdev import ecodes

print(os.getcwd())


async def print_events(device, channel):
    async for event in device.async_read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            print(device.path, evdev.categorize(event), sep=': ')


async def watch_keyboards():
    active_keyboards = {}
    while True:
        devices = [evdev.InputDevice(pth) for pth in evdev.list_devices()]
        chosen = ([
            d for d in devices if
            (
                    "Keyboard" in d.name and "Control" not in d.name
            )
        ])
        for d in chosen:
            path = d.path
            if path not in active_keyboards:
                dev = evdev.InputDevice(path)
                active_keyboards[path] = dev
                task = asyncio.create_task(print_events(dev, None))
                active_keyboards[path] = task
                print(f"\tAdding new keyboard: {path}")
        for path in active_keyboards:
            if active_keyboards[path].done():
                del active_keyboards[path]
                print(f"\tRemoving lost keyboard: {path}")



asyncio.ensure_future(watch_keyboards())

loop = asyncio.get_event_loop()
loop.run_forever()
