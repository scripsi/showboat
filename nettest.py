from machine import Pin

import time
import network
import urequests
import json

# configure with the following commands in the REPL:
#
# >>> import json
# >>> config={'wifissid':'[ssid]','wifipass':'[pass]','routeone':'[NN]','routetwo':'[NN]','checkinterval':'[NNs]'}
# >>> f = open('config.json', 'w')
# >>> f.write(json.dumps(config))
# >>> f.close()
#
f=open("config.json","r")
config=json.loads(f.read())
f.close()

status_url = 'http://status.calmac.info/?route=06'

onboard_led = Pin("LED", Pin.OUT)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config['wifissid'], config['wifipass'])

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
  if wlan.status() < 0 or wlan.status() >= 3:
    break
  max_wait -= 1
  onboard_led.toggle()
  print('waiting for connection...')
  time.sleep(1)

# Handle connection error
if wlan.status() != 3:
  onboard_led.off()
  raise RuntimeError('network connection failed')
else:
  print('connected')
  onboard_led.on()
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
