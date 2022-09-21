# showboat.py
#
# Copyright Douglas Reed 2022
#
# A script for showing CalMac ferry status on a Raspberry Pi Pico W

# *** IMPORTS ***
from machine import Pin
import time
import network
import urequests
import json

# *** CONSTANTS ***
GPIO_ROUTE1_GREEN = 15
GPIO_ROUTE1_YELLOW = 13
GPIO_ROUTE1_ORANGE = 9
GPIO_ROUTE1_RED = 5

GPIO_ROUTE2_GREEN = 16
GPIO_ROUTE2_YELLOW = 18
GPIO_ROUTE2_ORANGE = 22
GPIO_ROUTE2_RED = 28

STATUS_URL_PREFIX='http://status.calmac.info/?route='

ROUTE1 = 0
ROUTE2 = 1
NORMAL = 0
AWARE = 1
DISRUPTED = 2
CANCELLED = 3

leds = [[Pin(GPIO_ROUTE1_GREEN, Pin.OUT),
         Pin(GPIO_ROUTE1_YELLOW, Pin.OUT),
         Pin(GPIO_ROUTE1_ORANGE, Pin.OUT),
         Pin(GPIO_ROUTE1_RED, Pin.OUT)],
        [Pin(GPIO_ROUTE2_GREEN, Pin.OUT),
         Pin(GPIO_ROUTE2_YELLOW, Pin.OUT),
         Pin(GPIO_ROUTE2_ORANGE, Pin.OUT),
         Pin(GPIO_ROUTE2_RED, Pin.OUT)]]

# configure with the following commands in the REPL:
#
# >>> import json
# >>> config={'wifissid':'[ssid]','wifipass':'[pass]','routeone':'[NN]','routetwo':'[NN]','checkinterval':'[NNs]'}
# >>> f = open('config.json', 'w')
# >>> f.write(json.dumps(config))
# >>> f.close()
#

# Read config
f=open("config.json","r")
config=json.loads(f.read())
f.close()

status_url = 'http://status.calmac.info/?route=05'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config['wifissid'], config['wifipass'])

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
  if wlan.status() < 0 or wlan.status() >= 3:
    break
  max_wait -= 1
  leds[ROUTE1][NORMAL].toggle()
  print('waiting for connection...')
  time.sleep(1)

# Handle connection error
if wlan.status() != 3:
  leds[ROUTE1][NORMAL].off()
  raise RuntimeError('network connection failed')
else:
  print('connected')
  leds[ROUTE1][NORMAL].on()
  status = wlan.ifconfig()
  print( 'ip = ' + status[0] )

# Get status page
status_download = urequests.get(status_url)
status_message = str(status_download.content).lower()
status_download.close()

# Find service status
if 'normal service</h3>' in status_message:
  service_status="normal"
elif 'be aware</h3>' in status_message:
  service_status="aware"
elif 'disrupted</h3>' in status_message:
  service_status="disrupted"
elif 'remainder of today</h3>' in status_message:
  service_status="cancelled"
else:
  service_status="unknown"
print(service_status)
