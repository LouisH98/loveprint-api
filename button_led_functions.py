import RPi.GPIO as GPIO
from time import sleep
import math

pwm_intervals = 100
R = (pwm_intervals * math.log10(2)) / math.log10(100)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)
pwm = GPIO.PWM(18, 1000)
pwm.start(0)


def my_callback(channel):
    print("Button pressed!!")


def pulse_led():
    try:
        while True:  # Run forever
            brightness = 0

            for interval in range(0, pwm_intervals):
                brightness = math.pow(2, (interval / R)) - 1
                pwm.ChangeDutyCycle(brightness)
                sleep(0.02)

            for interval in range(pwm_intervals, 10, -1):
                brightness = math.pow(2, (interval / R)) - 1
                pwm.ChangeDutyCycle(brightness)
                sleep(0.02)
    except:
        GPIO.cleanup()


pulse_led()

# try:
#     while True: # Run forever
#
#         for brightness in range(0, 101):
#             pwm.ChangeDutyCycle(brightness)
#             sleep(0.02)
#
#         for brightness in range(100, -1, -1):
#             pwm.ChangeDutyCycle(brightness)
#             sleep(0.02)
# except KeyboardInterrupt:
#     GPIO.cleanup()
