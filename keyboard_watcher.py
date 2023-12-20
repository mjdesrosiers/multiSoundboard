import asyncio
import pprint
import random
import time
import pyudev
from pyudev import MonitorObserver


class EvdevTask:
    CONNECT = 0
    DISCONNECT = 1


async def udev_task(task_queue):
    n_tasks = 2000
    random.seed(0)
    tasks = [{"start": random.randint(1, 1000) / 10.0,
              "duration": random.randint(1, 1000) / 10.0,
              "started": False,
              "killed": False,
              "task": None} for _ in range(n_tasks)]
    start_time = time.time()

    active_keyboards = {}
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='input')

    def device_event(action, device):
        async def async_event(action, device):
            # TODO: filter down for non-control keyboards
            if action == "CONNECT":
                print(f"[udev] starting task = {device.device_node}")
                await task_queue.put([
                    EvdevTask.CONNECT,
                    device.device_node
                ])
            if action == "DISCONNECT":
                print(f"[udev] killing task = {device.device_node}")
                await task_queue.put([
                    EvdevTask.DISCONNECT,
                    device.device_node
                ])
        print('background event {0}: {1}'.format(action, device))
        asyncio.run(async_event(action, device))

    observer = MonitorObserver(monitor, device_event, name='monitor-observer')
    observer.start()

    while True:
        await asyncio.sleep(1)


async def evdev_task(task_queue):
    # this maybe should also test for existing devices as it starts
    # or do we just demand that the users power-cycle?
    tasks = {}
    while True:
        task_type, channel = await task_queue.get()
        if task_type == EvdevTask.CONNECT:
            print(f"\t[evdev]\tStarting task = {channel}")
            task = asyncio.create_task(keyboard_task(channel))
            tasks[channel] = task
        if task_type == EvdevTask.DISCONNECT:
            print(f"\t[evdev]\tKilling task = {channel}")
            task_to_kill = tasks.pop(channel)
            task_to_kill.cancel()


async def keyboard_task(channel):
    try:
        while True:
            print(f"\t\t[task]Ding! {channel}")
            await asyncio.sleep(10000)
    except asyncio.CancelledError:
        print(f"\t\t[task] cancelling {channel}")


if __name__ == "__main__":
    # inter-coroutine communication mechanism
    queue = asyncio.Queue()

    # define event loop for asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # start up and run tasks for connect/disconnect identification
    loop.create_task(udev_task(queue))
    loop.create_task(evdev_task(queue))

    # send it off to run
    loop.run_forever()
