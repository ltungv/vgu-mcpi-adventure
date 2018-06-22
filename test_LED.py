import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LEDs = [4, 17, 18, 27, 22, 23, 24, 13, 19, 26]
for led in LEDs:
    GPIO.setup(led, GPIO.OUT)


def led_timer(end_time, duration):
    timeleft = end_time - time.time()
    timeleft = int(timeleft * 10 / duration)
    for i in range(9, timeleft, -1):
        GPIO.output(LEDs[i], GPIO.LOW)


def reset_led_timer():
    for led in LEDs:
        GPIO.output(led, GPIO.HIGH)


is_reset = True
while True:
    if is_reset:
        reset_led_timer()
        reset_time = time.time() + 10
        is_reset = False
    led_timer(reset_time, 10)
    if time.time() >= reset_time:
        is_reset = True
