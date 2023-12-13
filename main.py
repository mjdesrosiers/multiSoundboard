import asyncio, evdev
from evdev import ecodes
import pygame

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

sound_map = {
    ecodes.KEY_KP0: "/sounds/sound0.wav",
    ecodes.KEY_KP1: "/sounds/sound1.wav",
    ecodes.KEY_KP2: "/sounds/sound2.wav",
    ecodes.KEY_KP3: "/sounds/sound3.wav",
    ecodes.KEY_KP4: "/sounds/sound4.wav",
    ecodes.KEY_KP5: "/sounds/sound5.wav",
    ecodes.KEY_KP6: "/sounds/sound6.wav",
    ecodes.KEY_KP7: "/sounds/sound7.wav",
    ecodes.KEY_KP8: "/sounds/sound8.wav",
    ecodes.KEY_KP9: "/sounds/sound9.wav",
}


async def print_events(device, channel):
    async for event in device.async_read_loop():
        if event.type == ecodes.EV_KEY:
            print(device.path, evdev.categorize(event), sep=': ')
        sound_path = sound_map.get(event.code)
        if sound_path:
            print(sound_path)


pygame.mixer.init()
for i, path in enumerate(device_paths):
    dev = evdev.InputDevice(path)
    channel = pygame.mixer.Channel(i)
    asyncio.ensure_future(print_events(dev, channel))

loop = asyncio.get_event_loop()
loop.run_forever()
