import board
import digitalio
import time
import os
import random
import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests

# *** CONSTANTS ***
GPIO_FIRST_ROUTE_GREEN = board.GP15
GPIO_FIRST_ROUTE_YELLOW = board.GP13
GPIO_FIRST_ROUTE_ORANGE = board.GP9
GPIO_FIRST_ROUTE_RED = board.GP5

GPIO_SECOND_ROUTE_GREEN = board.GP16
GPIO_SECOND_ROUTE_YELLOW = board.GP18
GPIO_SECOND_ROUTE_ORANGE = board.GP22
GPIO_SECOND_ROUTE_RED = board.GP28

VALID_ROUTE_CODES = ['01', # COWAL and DUNOON: Gourock (GOU) - Dunoon (DUN)
                     '02', # COWAL and KINTYRE: Tarbert, Lock Fyne (TLF) - Portavadie (POR)
                     '03', # BUTE: Wemyss Bay (WEM) - Rothesay (ROT)
                     '04', # BUTE: Colintraive (CTR) - Rhubodach (RHU)
                     '05', # ARRAN: Ardrossan (ARD) - Brodick (BRO)
                     '06', # ARRAN: Claonaig (CLA) - Lochranza (LRA)
                     '07', # CUMBRAE: Largs (LAR) - Millport, Cumbrae Slip (CUM)
                     '08', # GIGHA: Tayinloan (TAY) - Gigha (GIG)
                     '09', # ISLAY: Kennacraig (KEN) - Port Askaig (PAS) - Port Ellen (PEL)
                     '10', # COLONSAY: Oban (OBA) - Colonsay (CSA) - Port Askaig (PAS) - Kennacraig (KEN)
                     '11', # MULL: Oban (OBA) - Craignure (CRA)
                     '12', # MULL: Lochaline (LAL) - Fishnish (FIS)
                     '13', # IONA: Fionnphort (FIO) - Iona (ION)
                     '14', # ARDNAMURCHAN: Tobermory (TOB) - Kilchoan (KIC)
                     '15', # LISMORE: Oban (OBA) - Lismore (LIS)
                     '16', # COLL and TIREE: Oban (OBA) - Coll (CLL) - Tiree (TIR)
                     '17', # RAASAY: Sconser (SCO) - Raasay (RAA)
                     '18', # SKYE: Mallaig (MAL) - Armadale (ARM)
                     '19', # SMALL ISLES: Mallaig (MAL) - Small Isles (SIS)
                     '20', # BARRA: Oban (OBA) - Castlebay (CAS)
                     '21', # BARRA and ERISKAY: Ardmhor, Barra (AMH) - Eriskay (ERI)
                     '22', # NORTH UIST: Uig (UIG) - Lochmaddy (LMA)
                     '23', # NORTH UIST and HARRIS: Berneray (BER) - Leverburgh (LEV)
                     '24', # HARRIS: Uig (UIG) - Tarbert (TAR)
                     '25', # LEWIS: Ullapool (ULL) - Stornoway (STO)
                     '35', # LEWIS FREIGHT: Ullapool (ULL) - Stornoway (STO)
                     '37', # SOUTH UIST: Mallaig (MAL) - Lochboisdale (LBO)
                     '38', # KERRERA: Gallanach (GAL) - Kerrera (KER)
                     '39'] # KILCREGGAN and ROSNEATH: Gourock (GOU) - Kilcreggan (KIL)

STATUS_URL_PREFIX='http://status.calmac.info/?route='

FIRST_ROUTE = 0
SECOND_ROUTE = 1

# LED patterns for different conditions on each route
#   [Green,Yellow,Orange,Red]
ALL_ON = [True,True,True,True]
ALL_OFF = [False,False,False,False]

# Service status
NORMAL = [True,False,False,False]
AWARE = [False,True,False,False]
DISRUPTED = [False,False,True,False]
CANCELLED = [False,False,False,True]

# error conditions
CONFIG_ERROR = [False,True,True,True] # .YOR - Problem reading config - Have you set up the config file?
WIFI_ERROR = [False,False,True,True] # ..OR - Problem connecting to WiFi - Is it on? have you entered SSID and password correctly?
WEB_ERROR = [False,True,False,True] # .Y.R - Problem accessing CalMac status page - Check that it's live using another device
PARSE_ERROR = [False,True,True,False] # .YO. - Problem parsing status page - Has the format changed?


# *** GLOBAL VARIABLES ***
leds = [digitalio.DigitalInOut(GPIO_FIRST_ROUTE_GREEN),
        digitalio.DigitalInOut(GPIO_FIRST_ROUTE_YELLOW),
        digitalio.DigitalInOut(GPIO_FIRST_ROUTE_ORANGE),
        digitalio.DigitalInOut(GPIO_FIRST_ROUTE_RED),
        digitalio.DigitalInOut(GPIO_SECOND_ROUTE_GREEN),
        digitalio.DigitalInOut(GPIO_SECOND_ROUTE_YELLOW),
        digitalio.DigitalInOut(GPIO_SECOND_ROUTE_ORANGE),
        digitalio.DigitalInOut(GPIO_SECOND_ROUTE_RED)]

first_route_code = '00'
first_route_active = False
second_route_code = '00'
second_route_active = False

refresh_interval = 300

for led in leds:
  led.direction = digitalio.Direction.OUTPUT

# *** FUNCTION DEFINITIONS ***

def set_leds(route=FIRST_ROUTE,pattern=[False,False,False,False]):
  for l in range(4):
    leds[l + (route * 4)].value = pattern[l]

def get_status(route=FIRST_ROUTE,message=""):
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

print("Starting Showboat!")

# Startup animation
set_leds(FIRST_ROUTE,CANCELLED)
set_leds(SECOND_ROUTE,CANCELLED)
time.sleep(0.2)
set_leds(FIRST_ROUTE,DISRUPTED)
set_leds(SECOND_ROUTE,DISRUPTED)
time.sleep(0.2)
set_leds(FIRST_ROUTE,AWARE)
set_leds(SECOND_ROUTE,AWARE)
time.sleep(0.2)
set_leds(FIRST_ROUTE,NORMAL)
set_leds(SECOND_ROUTE,NORMAL)
time.sleep(0.2)
set_leds(FIRST_ROUTE,ALL_ON)
set_leds(SECOND_ROUTE,ALL_ON)
time.sleep(0.5)
set_leds(FIRST_ROUTE,ALL_OFF)
set_leds(SECOND_ROUTE,ALL_OFF)


# Check for config file
print("Checking for config file")
try:
  open("/.env","r")
except:
  set_leds(FIRST_ROUTE,CONFIG_ERROR)
  set_leds(SECOND_ROUTE,CONFIG_ERROR)
  time.sleep(10)
  raise RuntimeError("Couldn't read config")

# Read config file
if os.getenv('FIRST_ROUTE_CODE') in VALID_ROUTE_CODES:
  first_route_code = os.getenv('FIRST_ROUTE_CODE')
  first_route_active = True

if os.getenv('SECOND_ROUTE_CODE') in VALID_ROUTE_CODES:
  second_route_code = os.getenv('SECOND_ROUTE_CODE')
  second_route_active = True

refresh_interval = max(60, int(os.getenv('REFRESH_INTERVAL')))

# Open WiFi
print("Connecting to WiFi")
wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))

print("Connected to WiFi")

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

#  prints IP address to REPL
print("My IP address is", wifi.radio.ipv4_address)

while True:
  if first_route_active:
    try:
      response = requests.get(STATUS_URL_PREFIX + first_route_code)
      get_status(FIRST_ROUTE, response.text.lower())
      response.close()
    except Exception as e:
      print("Error:\n", str(e))
  if second_route_active:
    try:
      response = requests.get(STATUS_URL_PREFIX + second_route_code)
      get_status(SECOND_ROUTE, response.text.lower())
      response.close()
    except Exception as e:
      print("Error:\n", str(e))
  time.sleep(random.randint(refresh_interval-10,refresh_interval+10))
