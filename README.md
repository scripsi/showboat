# ShowBoat

A small display to show CalMac ferry status

## Introduction

This is a small project using the Raspberry Pi Pico W to show the service status of Scottish ferries on the Caledonian MacBrayne network. The intention is to create a small and cheap (<£10) device that can show at a glance if a particular ferry service is running normally or is disrupted. The hardware design should be cheap and relatively easy for a hobbyist to build. I describe the development process in more detail in [development.md](development.md)

## Hardware

- Raspberry Pi Pico W

- 2 each x green, yellow, orange and red 3mm through-hole LEDs

- 8 x 100-330 Ohm resistors

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

This is a very simple circuit. The cathodes of the LEDs are connected directly to the four ground pads down each side of the Pico W (marked by square-ended pads), and the anodes are connected via current limiting resistors to GPIO pads. **Just make sure that the short lead and/or flat side of each LED (the cathode) is connected to ground on the Pico W and the long lead (anode) is connected via a resistor to one of the GPIO**.
