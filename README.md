# showboat

A small display to show CalMac ferry status

## Introduction

This is a small project using the Raspberry Pi Pico W to show the service status of Scottish ferries on the Caledonian MacBrayne network. The intention is to create a small and cheap (<£10) device that can show at a glance if a particular ferry service is running normally or is disrupted.



Caledonian MacBrayne ("CalMac") have a network of ferries serving the Western Isles and islands in the Clyde Estuary in Scotland. These are considered "lifeline" services for the islands that they sail to, and any disruption to sailings can cause significant problems for both islanders and visitors. Disruption can be caused by weather, equipment failure, routine maintenance, and even tidal conditions. Knowing about disruption as soon as possible helps ferry users to make alternative plans.



CalMac provides a service status page on their website and an app for Android and Apple devices, as well as an SMS notification service that regular ferry users can subscribe to. These services cover all of the CalMac routes. Most ferry users are only interested in the one or two routes that serve their own island. I wanted to make a simple hardware indicator that could show, at a glance, the service status on the routes that serve a particular location. The hardware design should be cheap and relatively easy for a hobbyist to build.

## Hardware

- Raspberry Pi Pico W

- Green, yellow, orange and red 3mm through-hole LEDs

- 100 Ohm resistors

- 3D printed case

The LEDs that I am using have the following characteristics:

| Value | Red  | Orange | Yellow | Green |
| ----- | ---- | ------ | ------ | ----- |
| V~f~  | 1.9V | 1.9V   | 2.0V   | 2.1V  |
| I~f~  | 30mA | 30mA   | 20mA   | 30mA  |

Using the normal formula for calculating the correct current limiting resistor at the Pico's voltage of 3.3V gives values in the range 40-65 Ohms, so using 100 Ohm resistors should be safe enough while keeping the LEDs nice and bright.
