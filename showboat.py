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

# LED patterns for different conditions on each route
#   [Green,Yellow,Orange,Red]
ALL_ON = [1,1,1,1]
ALL_OFF = [0,0,0,0]

# Service status
NORMAL = [1,0,0,0]
AWARE = [0,1,0,0]
DISRUPTED = [0,0,1,0]
CANCELLED = [0,0,0,1]

# error conditions
CONFIG_ERROR = [0,1,1,1] # xYOR - Problem reading config - Have you set up config file? (see below)
WIFI_ERROR = [0,0,1,1] # xxOR - Problem connecting to WiFi - Is it on? have you entered SSID and password correctly?
WEB_ERROR = [0,1,0,1] # xYxR - Problem accessing CalMac status page - Check that it's live using another device
PARSE_ERROR = [0,1,1,0] # xYOx - Problem parsing status page - Has the format changed?

# *** GLOBAL VARIABLES ***
leds = [Pin(GPIO_ROUTE1_GREEN, Pin.OUT),
        Pin(GPIO_ROUTE1_YELLOW, Pin.OUT),
        Pin(GPIO_ROUTE1_ORANGE, Pin.OUT),
        Pin(GPIO_ROUTE1_RED, Pin.OUT),
        Pin(GPIO_ROUTE2_GREEN, Pin.OUT),
        Pin(GPIO_ROUTE2_YELLOW, Pin.OUT),
        Pin(GPIO_ROUTE2_ORANGE, Pin.OUT),
        Pin(GPIO_ROUTE2_RED, Pin.OUT)]

refresh_interval = 300

# *** FUNCTION DEFINITIONS ***

def set_leds(route=ROUTE1,pattern=[0,0,0,0]):
  for l in range(4):
    leds[l + (route * 4)].value(pattern[l])
    
def get_status(route=ROUTE1,message=""):
  if 'normal service</h3>' in message:
    set_leds(route,NORMAL)
    print('Route ', route + 1, ': Normal service')
  elif 'be aware</h3>' in message:
    set_leds(route,AWARE)
    print('Route ', route + 1, ': Be aware')
  elif 'disrupted</h3>' in message:
    set_leds(route,DISRUPTED)
    print('Route ', route + 1, ': Service disrupted')
  elif 'remainder of today</h3>' in message:
    set_leds(route,CANCELLED)
    print('Route ', route + 1, ': Service cancelled')
  else:
    set_leds(route,PARSE_ERROR)
    print("Route ", route + 1, ": Couldn't parse status message")

# *** INITIALISATION ***

# Startup animation
set_leds(ROUTE1,[0,0,0,1])
set_leds(ROUTE2,[0,0,0,1])
time.sleep(0.25)
set_leds(ROUTE1,[0,0,1,1])
set_leds(ROUTE2,[0,0,1,1])
time.sleep(0.25)
set_leds(ROUTE1,[0,1,1,1])
set_leds(ROUTE2,[0,1,1,1])
time.sleep(0.25)
set_leds(ROUTE1,ALL_ON)
set_leds(ROUTE2,ALL_ON)
time.sleep(1)

# configure with the following commands in the REPL:
#
# >>> import json
# >>> config={'wifissid':'[ssid]','wifipass':'[pass]','routeone':'[NN]','routetwo':'[NN]'}
# >>> f = open('config.json', 'w')
# >>> f.write(json.dumps(config))
# >>> f.close()
#

# Read config

try:
  f=open("config.json","r")
  config=json.loads(f.read())
  f.close()
except:
  set_leds(ROUTE1,CONFIG_ERROR)
  set_leds(ROUTE2,CONFIG_ERROR)
  raise RuntimeError("Couldn't read config")

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config['wifissid'], config['wifipass'])

# Wait for connection
while True:
  if wlan.status() < 0 or wlan.status() >= 3:
    break
  print('waiting for connection...')
  time.sleep(1)

# Handle connection error
if wlan.status() != 3:
  set_leds(ROUTE1,WIFI_ERROR)
  set_leds(ROUTE2,WIFI_ERROR)
  raise RuntimeError('Network connection failed')
else:
  print('connected')
  wlan_status = wlan.ifconfig()
  print( 'ip = ' + wlan_status[0] )

set_leds(ROUTE1,ALL_OFF)
set_leds(ROUTE2,ALL_OFF)

# *** MAIN LOOP ***
while True:
  # Get route 1 status page
  try:
    route1_download = urequests.get(STATUS_URL_PREFIX + config['routeone'])
  except:
    set_leds(ROUTE1,WEB_ERROR)
    print("Couldn't download route 1 status")
  else:
    get_status(ROUTE1, str(route1_download.content).lower())
    route1_download.close()
  if config['routetwo'] != "00":
    try:
      route2_download = urequests.get(STATUS_URL_PREFIX + config['routetwo'])
    except:
      set_leds(ROUTE2,WEB_ERROR)
      print("Couldn't download route 2 status")
    else:
      get_status(ROUTE2, str(route2_download.content).lower())
      route2_download.close()
      
  time.sleep(refresh_interval)

