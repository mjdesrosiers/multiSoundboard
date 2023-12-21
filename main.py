import asyncio, evdev
import os
import RPi.GPIO as GPIO

from evdev import ecodes
import pygame

from SystemStatus import SystemStatus

print(os.getcwd())


def get_connected_keyboards():
    global path, dev, device_paths
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for dev in devices:
        print(dev.name)
    chosen = ([
        dev for dev in devices if
        (
                ("Keyboard" in dev.name or "Wireless Receiver" in dev.name) and "Control" not in dev.name
        )
    ])
    device_paths = [dev.path for dev in chosen]
    return device_paths


device_paths = get_connected_keyboards()
print(device_paths)
assert len(device_paths)

START_VOLUME = 0.1

pygame.mixer.init()
pygame.mixer.set_num_channels(16)
channel_noise = pygame.mixer.Channel(0)
channel_volume_update = pygame.mixer.Channel(1)

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
    sound.set_volume(START_VOLUME)
    sound_map[k] = sound

volume_update_sound = pygame.mixer.Sound('./sounds/click.mp3')
volume_update_sound.set_volume(START_VOLUME)


def volume_change(amount):
    for key in sound_map:
        sound = sound_map[key]
        volume_current = sound.get_volume()
        volume_new = volume_current + amount
        volume_current = min(volume_current, 1.0)
        volume_current = max(volume_current, 0)
        sound.set_volume(volume_new)
        print(f"Changed volume from {volume_current} to {volume_new}")
    volume_current = volume_update_sound.get_volume()
    volume_current += amount
    volume_current = min(volume_current, 1.0)
    volume_current = max(volume_current, 0)
    volume_update_sound.set_volume(volume_current)
    channel_volume_update.play(volume_update_sound)


action_map = {
    ecodes.KEY_KPPLUS: (volume_change, 0.1),
    ecodes.KEY_KPMINUS: (volume_change, -0.1)
}


async def play_noise(channel):
    path_noise = "./sounds/noise.mp3"
    sound = pygame.mixer.Sound(path_noise)
    sound.set_volume(0.01)
    channel.play(sound, -1)


async def watch_keyboard(device, audio_channel, status_queue):
    async for event in device.async_read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            print(device.path, evdev.categorize(event), sep=': ')
        sound = sound_map.get(event.code)
        if sound and event.value == 1:
            audio_channel.play(sound)
            await status_queue.put(SystemStatus.Playing)
        action, param = action_map.get(event.code, (None, None))
        if action and event.value == 1:
            action(param)


async def update_pwm_status(pwm_pin, pwm_queue):
    status = SystemStatus.Idle
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pwm_pin, GPIO.OUT)
    pwm = GPIO.PWM(pwm_pin, 1)
    while True:
        pwm.ChangeFrequency(status.freq)
        pwm.start()
        try:
            async with asyncio.timeout(status.timeout):
                status = await pwm_queue.get()
        except TimeoutError:
            status = SystemStatus.Idle

status_queue = asyncio.Queue()

for i, path in enumerate(device_paths):
    dev = evdev.InputDevice(path)
    mixer_channel = pygame.mixer.Channel(i + 2)
    asyncio.ensure_future(watch_keyboard(dev, mixer_channel, status_queue))

asyncio.ensure_future(update_pwm_status(20, status_queue))
# asyncio.ensure_future(play_noise(channel_noise))

loop = asyncio.get_event_loop()
loop.run_forever()
