import asyncio, evdev


devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

chosen = ([
            dev for dev in devices if
            (
                    "Keyboard" in dev.name and "Control" not in dev.name
            )
          ])

device_paths = [dev.path for dev in chosen]

print(device_paths)

assert len(device_paths)

async def print_events(device):
    async for event in device.async_read_loop():
        print(device.path, evdev.categorize(event), sep=': ')

for device in device_paths:
    asyncio.ensure_future(print_events(evdev.InputDevice(device)))

loop = asyncio.get_event_loop()
loop.run_forever()