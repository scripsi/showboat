# showboat

A small display to show CalMac ferry status

## Introduction

This is a small project using the Raspberry Pi Pico W to show the service status of Scottish ferries on the Caledonian MacBrayne network. The intention is to create a small and cheap (<£10) device that can show at a glance if a particular ferry service is running normally or is disrupted.

Caledonian MacBrayne ("CalMac") have a network of ferries serving the Western Isles and islands in the Clyde Estuary in Scotland. These are considered "lifeline" services for the islands that they sail to, and any disruption to sailings can cause significant problems for both islanders and visitors. Disruption can be caused by weather, equipment failure, routine maintenance, and even tidal conditions. Knowing about disruption as soon as possible helps ferry users to make alternative plans.

CalMac provides a service status page on their website and an app for Android and Apple devices, as well as an SMS notification service that regular ferry users can subscribe to. These services cover all of the CalMac routes. Most ferry users are only interested in the one or two routes that serve their own island. I wanted to make a simple hardware indicator that could show, at a glance, the service status on the routes that serve a particular location. The hardware design should be cheap and relatively easy for a hobbyist to build.

## Hardware

- Raspberry Pi Pico W

- 2 each x green, yellow, orange and red 3mm through-hole LEDs

- 8 x 100 Ohm resistors

The LEDs that I am using have the following characteristics:

| Value | Red  | Orange | Yellow | Green |
| ----- | ---- | ------ | ------ | ----- |
| Vf    | 1.9V | 1.9V   | 2.0V   | 2.1V  |
| If    | 30mA | 30mA   | 20mA   | 30mA  |

Using an [LED calculator](http://ledcalc.com/) for the correct current limiting resistor at the Pico's voltage of 3.3V gives values in the range 40-65 Ohms, so using 100 Ohm resistors should be safe enough while keeping the LEDs nice and bright. If you use LEDs with different characteristics, choose appropriate current-limiting resistors for them, using a supply voltage of 3.3V.

## Schematic

```
            ___________________________
RESISTOR----)21 GP16           GP15 20(----RESISTOR
    |       )22 GP17           GP14 19(       |
 GREEN LED--]23 GND             GND 18[--GREEN LED
    .-------)24 GP18           GP13 17(-------.
    |       )25 GP19           GP12 16(       |
RESISTOR    )26 GP20           GP11 15(    RESISTOR
    |       )27 GP21           GP10 14(       |
YELLOW LED--]28 GND             GND 13[--YELLOW LED
    .-------)29 GP22            GP9 12(-------.
    |       )30 RUN   PICO W    GP8 11(       |
RESISTOR    )31 GP26            GP7 10(    RESISTOR
    |       )32 GP27            GP6  9(       |
ORANGE LED--]33 GND             GND  8[--ORANGE LED
    .-------)34 GP28            GP5  7(-------.
    |       )35 ADC_VREF        GP4  6(       |
RESISTOR    )36 3V3             GP3  5(    RESISTOR
    |       )37 3V3_EN          GP2  4(       |
   RED LED--]38 GND   _______   GND  3[--RED LED
            )39 VSYS  |     |   GP1  2(
            )40 VBUS__| USB |___GP0  1(
                      |_____|           
```

This is a very simple circuit. The cathodes of the LEDs are connected directly to the four  ground pads down each side of the Pico W (marked by square-ended pads), and the anodes are connected via current limiting resistors to GPIO pads.

![The front of the prototype with two colums of LEDs](img/prototype-front.jpg)

![The rear of the prototype with the resistors and Pico W](img/prototype-rear.jpg)

I used a small protoboard for my prototype (with a socketed Pico W), with the LEDs mounted on the front and the resistors and Pico W mounted on the rear to keep things looking clean. Arranging the LEDs according to the evenly-spaced ground pads on the Pico W resulted in two neat columns of indicator lights which could be used for the two different ferry routes. The Pico W had its USB port facing downwards because I imagined the device eventually hanging on a wall with the USB power supply cable dangling down from it.

![The prototype board - closeup showing solder joints](img/prototype-board.jpg)

You could always use a different arrangement, and to keep things even simpler it should be possible to solder the components directly onto the Pico W [dead bug style](https://www.instructables.com/Dead-Bug-Prototyping-and-Freeform-Electronics/). **Just make sure that the short lead and/or flat side of each LED (the cathode) is connected to ground on the Pico W and the long lead (anode) is connected via a resistor to one of the GPIO**. 
