# Developing ShowBoat

## Introduction

Caledonian MacBrayne ("CalMac") have a network of ferries serving the Western Isles and islands in the Clyde Estuary in Scotland. These are considered "lifeline" services for the islands that they sail to, and any disruption to sailings can cause significant problems for both islanders and visitors. Disruption can be caused by weather, equipment failure, routine maintenance, and even tidal conditions. Knowing about disruption as soon as possible helps ferry users to make alternative plans.

CalMac provides a service status page on their website and an app for Android and Apple devices, as well as an SMS notification service that regular ferry users can subscribe to. These services cover all of the CalMac routes. Most ferry users are only interested in the one or two routes that serve their own island. I wanted to make a simple hardware indicator that could show, at a glance, the service status on the routes that serve a particular location.

While I was initially making this just for my own use, I thought that other people might also find it helpful, so I wanted to keep the design relatively cheap and straightforward. The Raspberry Pi Foundation had just launched the Raspberry Pi Pico W, which opened up the possibility of making a very cheap, Internet-connected device to show simple status information.

## Design considerations

### How to display service status?

The real-time service information provided by CalMac uses four different status levels for each route:

![CalMac status levels](/home/douglas/scripsi/showboat/img/calmac-status-types.png)

These status levels are distinguished by three different design features:

- Text description

- Symbol (tick, exclamation mark(s), cross)

- Colour (green, yellow, amber, red)

My project could use any or all of these design features to represent the service status, however the choice of features would have a big effect on the cost and complexity of the project: 

- a text status would require a display that could show at least 36 characters (the longest phrase) at a size that was readable across a room - such a display would be relatively expensive and might have high power requirements.

- A status symbol could be displayed by a matrix of LEDs, either single-color or RGB, but matrices of sufficient size are still fairly costly and complex to drive. A symbol could also be illuminated from behind by an LED, but this would make the enclosure design much more complex.

- A colour status could be represented by a single analogue or digitally-addressable RGB LED, or by a column of different single-colour LEDs. The problem with using a single LED was that I found it could be hard to distinguish between some colours ("is that yellow or amber?"). Using a column of single-colour LEDs showed the status using both colour _and_ position and so was easier to read correctly at a glance. Although this increased the component count, those components were so cheap that it was still the best and lowest-cost option.

The other factor that led me to the "column-of-LEDs" approach was the physical design of the Raspberry Pi Pico W that I wanted to use. The regular ordering and spacing of the GPIO and ground pads in symmetrical columns down each side of the device really helps with this project!

_Side note_: The CalMac status page also shows a "Supplementary Information" indicator by each route status. This used to warn of indirect issues, such as road closures on the routes to ports, and was quite helpful, but since COVID19 it seems that _every_ route has supplementary information _all the time_, so it has lost its usefulness as an indicator. I decided not to worry about trying to include a "Supplementary Information" indicator in this project!

### How many routes?

The full CalMac network has 29 different routes but it is not necessary to show the status of all of these routes for a particular location. Most islands are served by only one or two routes  (though some mainland ports may serve more routes than this). I've assumed that showing the status of only one or two routes should be sufficient for most people. The Raspberry Pi Pico W has sufficient GPIO to show up to 6 routes with four status LEDs each, but showing more than 2 routes would require a more complex design involving some sort of extra circuit board.

### Obtaining service status

CalMac offers three main methods of checking their service status:

- On their website at [https://www.calmac.co.uk/service-status](https://www.calmac.co.uk/service-status)

- Using their [Android](http://play.google.com/store/apps/details?id=com.CalMacStatus) or [Apple](http://itunes.apple.com/us/app/directv/id396345728?mt=8) app

- By signing up to an SMS alert service

The SMS alert service would not be useful for me, but I thought the other two methods must use some form of IP network communication which should be possible to exploit with the Pico W. A bit of judicious analysis of web page code and traffic sniffing reveals a very simple API that serves the status information to both the web page and apps via two different URLs:

- *https://www.calmac.co.uk/service-status/{query}* for the full website

or

- *http://status.calmac.info/{query}* for the app

The _{query}_ can take one of three forms:

- [blank] - default response with an HTML page summarising the status of all routes

- _?route=NN_ - responds with an HTML page containing detailed information about a single route. _NN_ is the two digit text code for the route as shown on the summary status page 

- *?ajax=json* - responds with JSON-encoded information for ALL routes

So far I have only been able to get one of these three things. Any attempt to combine parameters to refine the query (eg _ajax=json&route=05_) just responds with the default status page for all routes, as if I had left the query blank.

The HTML responses from the two URLs were different, while the JSON responses were identical from both URLs. Here's some analysis of file download sizes for different queries at a particular date and route:

|                                           | [blank]  | ?route=05 | ?ajax=json |
| ----------------------------------------- | -------- | --------- | ---------- |
| *http://www.calmac.co.uk/service-status/* | 73.5 kB  | 34.9 kB   | 48.1 kB    |
| *http://status.calmac.info/*              | 135.8 kB | 4.6 kB    | 48.1 kB    |

In general, the responses are quite large. The JSON responses contain full information about all routes, including all the supplementary notes, and there is apparently no way to refine or filter that information. The HTML responses are generally rather large because they contain a lot of extra design info and scripts. Once loaded, the default web status page downloads and parses the entire JSON response every 10 seconds to update its list of routes. The default app status page has a leaner general design but it already incorporates the full service info, rather than downloading it separately, and so is even larger. This is _not_ a very efficient API!

Ideally, I would like to use the JSON data from the API, because it would be easy to parse. Unfortunately, the download size is so large that the Pico W doesn't have enough memory to cope, and so I can't use it! Instead I will have to obtain the info from the individual route status pages which (in the case of the app URL at least) are actually small enough for the Pico W to load.

Scraping an HTML page for data is not ideal - trivial design or content changes can easily break the parsing of the information you're interested in. The CalMac web page design doesn't help, either. The HTML element containing the status info isn't given a unique CSS ID or class, so there is no simple way to isolate it. In the end I have to search the web page text for the particular phrases used for each service status. These phrases appear in an h3 element near the top of the page.

## Hardware Prototype

The LEDs that I used for the prototype had the following characteristics:

| Value | Red  | Orange | Yellow | Green |
| ----- | ---- | ------ | ------ | ----- |
| Vf    | 1.9V | 1.9V   | 2.0V   | 2.1V  |
| If    | 30mA | 30mA   | 20mA   | 30mA  |

Using an [LED calculator](http://ledcalc.com/) for the correct current limiting resistor at the Pico's voltage of 3.3V gave values in the range 40-65 Ohms, so I thought that using 100 Ohm resistors should be safe enough while keeping the LEDs nice and bright. This was a bit too successful - the green LEDs in particular were so bright they could light up a darkened room! They were difficult to look at straight on - I thought it was necessary to tone them down a bit for the final version by using 200-300 Ohm resistors.

![The prototype board - closeup showing solder joints](img/prototype-board.jpg)

I used a small protoboard for my prototype (with a socketed Pico W), with the LEDs mounted on the front and the resistors and Pico W mounted on the rear to keep things looking clean. Arranging the LEDs according to the evenly-spaced ground pads on the Pico W resulted in two neat columns of indicator lights which could be used for the two different ferry routes. The Pico W had its USB port facing downwards because I imagined the device eventually hanging on a wall with the USB power supply cable dangling down from it.

![The front of the prototype with two colums of LEDs](img/prototype-front.jpg)

![The rear of the prototype with the resistors and Pico W](img/prototype-rear.jpg)

I made a temporary enclosure for the prototype out of a small cardboard box (from an official Raspberry Pi power supply, I think). You could always use a different arrangement, and to keep things even simpler it should be possible to solder the components directly onto the Pico W [dead bug style](https://www.instructables.com/Dead-Bug-Prototyping-and-Freeform-Electronics/).

## Software Design

The software on the Pico W will have to perform the following tasks:

- Read in configuration info about the local WiFi network and the particular CalMac routes to be monitored

- Connect to the WiFi network

- Repeatedly poll CalMac's servers, parse the responses for the current route status information and light the appropriate LEDs

- Report any errors using LED patterns 

That first task presents an immediate problem: _how to set the configuration info so that it can be read in by the software_.

### Configuration

In order for my project to be widely usable, it must be easy for a relatively non-technical person to set up and use. The acid test is: if I build a device and send it to my (hypothetical) aunt in Stornoway or my (equally hypothetical) uncle on Mull, will she or he be able to set it up themselves on their own WiFi networks (which I might not have details of) and configure it for the CalMac routes they are interested in? If they subsequently change their network details or move to a different island, will they be able to update the configuration to keep it working?

Potential configuration solutions partly depend on which programming language you are using to write the software. The officially supported languages on the Pico W are C and MicroPython. I'm not a C programmer, and MicroPython is a pain to configure (though see my change of heart later on!) With MicroPython, the internal storage of the Pico W is only accessible through a serial console, so only dedicated MicroPython IDEs like Mu or Thonny can save to it easily. I didn't want to force people to install special software on their computers (if they even _have_ computers) just in order to set up my device!

An alternative was to use CircuitPython instead. Although not officially supported on the Pico W, Adafruit's CircuitPython is very well documented and easy to use, and the very latest version is compatible with the Pico W. CircuitPython presents the Pico W storage as a standard USB drive that you can read or save to with ordinary file tools. This makes it very easy to use for prototyping, but it also makes it quite easy to configure. Environment variables can be set in a file called ".env" and these values can easily be used in your code. So, as long as my hypothetical aunt and uncle can deal with editing a text file on a USB drive, then they can set up and reconfigure the device. But even that may be too difficult for some users, who may not have a computer at all or who may not be confident in editing a config file correctly.

So I have not yet solved the configuration problem, though one avenue looks promising: The lovely people at [Pimoroni](https://shop.pimoroni.com/) have realeased a set of hardware sensors called "Enviro" that are driven by an attached Pico W. They produced a rather nice provisioning routine that goes like this:

- When first run, the Pico W creates its own WiFi network

- User connects to Pico's WiFi network with a phone, tablet, computer etc and opens a configuration web page.

- User sets their own WiFi network details (SSID and password) plus any other necessary configuration

- The Pico W reboots, connects to the user's WiFi and runs the main software using the saved configuration info

This is quite a common paradigm for setting up small, Internet-connected devices these days, so it should be familiar to most people. Pimoroni have produced a rather nice MicroPython web library to help with this called [Phew!](https://github.com/pimoroni/phew), which I want to explore further. 

The downside to this idea is that in order to reconfigure the device later on you either need to reinstall the firmware from scratch or press a button while restarting the device to trigger the provisioning routine again. Adding an extra button to my very simplistic hardware design would be difficult because I've already used up the available ground pins on the edge of the Pico W!