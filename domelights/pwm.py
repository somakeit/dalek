import RPi.GPIO as GPIO

PWM_PIN = 18
ALL_PINS = [PWM_PIN]
pwm = None

def init():
    global pwm
    GPIO.setmode(GPIO.BCM)

    for port in ALL_PINS:
        GPIO.setup(port, GPIO.OUT)

    pwm = GPIO.PWM(PWM_PIN, 50)
    pwm.start(0)

def write(value):
    val = round(value * 100.0)
    pwm.ChangeDutyCycle(val)
