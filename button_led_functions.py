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



while True: # Run forever
    brightness = 0

    for interval in range(0, pwm_intervals):
        brightness = math.pow(2, (interval / R)) - 1
        pwm.ChangeDutyCycle(brightness)
        sleep(0.015)

    for interval in range(pwm_intervals, -1, -1):
        brightness = math.pow(2, (interval / R)) - 1
        # brightness = 0 if brightness < 0.5 else brightness
        # print(brightness)

        pwm.ChangeDutyCycle(brightness)
        sleep(0.015)

