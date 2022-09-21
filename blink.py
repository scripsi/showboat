from machine import Pin
from time import sleep

# *** CONSTANTS ***
GPIO_ROUTE1_GREEN = 15
GPIO_ROUTE1_YELLOW = 13
GPIO_ROUTE1_ORANGE = 9
GPIO_ROUTE1_RED = 5

GPIO_ROUTE2_GREEN = 16
GPIO_ROUTE2_YELLOW = 18
GPIO_ROUTE2_ORANGE = 22
GPIO_ROUTE2_RED = 28

onboard_led = Pin("LED", Pin.OUT)

green1_led = Pin(GPIO_ROUTE1_GREEN, Pin.OUT)
yellow1_led = Pin(GPIO_ROUTE1_YELLOW, Pin.OUT)
orange1_led = Pin(GPIO_ROUTE1_ORANGE, Pin.OUT)
red1_led = Pin(GPIO_ROUTE1_RED, Pin.OUT)

green2_led = Pin(GPIO_ROUTE2_GREEN, Pin.OUT)
yellow2_led = Pin(GPIO_ROUTE2_YELLOW, Pin.OUT)
orange2_led = Pin(GPIO_ROUTE2_ORANGE, Pin.OUT)
red2_led = Pin(GPIO_ROUTE2_RED, Pin.OUT)

while True:
    onboard_led.toggle()
    green1_led.toggle()
    green2_led.toggle()
    sleep(0.5)
    yellow1_led.toggle()
    yellow2_led.toggle()
    sleep(0.5)
    orange1_led.toggle()
    orange2_led.toggle()
    sleep(0.5)
    red1_led.toggle()
    red2_led.toggle()
    sleep(1)