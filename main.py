import asyncio, evdev
import os

from evdev import ecodes
import pygame

print(os.getcwd())

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
    ecodes.KEY_KP0: "sounds/fart.mp3",
    ecodes.KEY_KP1: "sounds/fart.mp3",
    ecodes.KEY_KP2: "sounds/fart.mp3",
    ecodes.KEY_KP3: "sounds/fart.mp3",
    ecodes.KEY_KP4: "sounds/fart.mp3",
    ecodes.KEY_KP5: "sounds/fart.mp3",
    ecodes.KEY_KP6: "sounds/fart.mp3",
    ecodes.KEY_KP7: "sounds/fart.mp3",
    ecodes.KEY_KP8: "sounds/fart.mp3",
    ecodes.KEY_KP9: "sounds/fart.mp3",
}


async def print_events(device, channel):
    async for event in device.async_read_loop():
        if event.type == ecodes.EV_KEY:
            print(device.path, evdev.categorize(event), sep=': ')
        sound_path = sound_map.get(event.code)
        if sound_path and event.value == 1:
            print(sound_path)
            channel.play(pygame.mixer.Sound(sound_path))


pygame.mixer.init()
for i, path in enumerate(device_paths):
    dev = evdev.InputDevice(path)
    mixer_channel = pygame.mixer.Channel(i)
    asyncio.ensure_future(print_events(dev, mixer_channel))

loop = asyncio.get_event_loop()
loop.run_forever()
