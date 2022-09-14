from machine import Pin
from time import sleep

onboard_led = Pin("LED", Pin.OUT)
green_led = Pin(0, Pin.OUT)
yellow_led = Pin(1, Pin.OUT)
orange_led = Pin(2, Pin.OUT)
red_led = Pin(3, Pin.OUT)

while True:
    onboard_led.toggle()
    green_led.toggle()
    yellow_led.toggle()
    orange_led.toggle()
    red_led.toggle()
    sleep(1)