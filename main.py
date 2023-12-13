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

volume = 0.3

sound_map = {
    ecodes.KEY_KP0: "./sounds/fart.mp3",
    ecodes.KEY_KP1: "./sounds/fart.mp3",
    ecodes.KEY_KP2: "./sounds/fart.mp3",
    ecodes.KEY_KP3: "./sounds/fart.mp3",
    ecodes.KEY_KP4: "./sounds/fart.mp3",
    ecodes.KEY_KP5: "./sounds/fart.mp3",
    ecodes.KEY_KP6: "./sounds/fart.mp3",
    ecodes.KEY_KP7: "./sounds/fart.mp3",
    ecodes.KEY_KP8: "./sounds/fart.mp3",
    ecodes.KEY_KP9: "./sounds/skillissue.mp3",
}

for k in sound_map:
    path = sound_map[k]
    sound = pygame.mixer.Sound(path)
    sound.set_volume(0.2)
    sound_map[k] = sound

path_noise = "./sounds/noise.mp3"

async def play_noise(channel, noise_path):
    sound = pygame.mixer.Sound(noise_path)
    sound.set_volume(0.005)
    channel.play(sound, -1)
    # channel_noise.set_volume(0.1)

async def print_events(device, channel):
    async for event in device.async_read_loop():
        if event.type == ecodes.EV_KEY:
            print(device.path, evdev.categorize(event), sep=': ')
        sound = sound_map.get(event.code)
        if sound and event.value == 1:
            channel.play(sound)


pygame.mixer.init()
channel_noise = pygame.mixer.Channel(0)


for i, path in enumerate(device_paths):
    dev = evdev.InputDevice(path)
    mixer_channel = pygame.mixer.Channel(i + 1)
    asyncio.ensure_future(print_events(dev, mixer_channel))

asyncio.ensure_future(play_noise(channel_noise, path_noise))

loop = asyncio.get_event_loop()
loop.run_forever()
