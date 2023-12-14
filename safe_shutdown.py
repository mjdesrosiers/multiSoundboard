from subprocess import call
import datetime

PIN_SHUTDOWN_CHECK = 5

def is_shutdown_condition_triggered():
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_SHUTDOWN_CHECK, GPIO.IN)
        value = GPIO.input(PIN_SHUTDOWN_CHECK)
        return not value
    except:
        return True

should_shutdown = is_shutdown_condition_triggered()

with open("shutdown_log.txt", "a") as f:
    f.write(f"{datetime.datetime.now()}\tShutdown = {should_shutdown}")

if should_shutdown:
    call("sudo nohup shutdown -h now", shell=True)
