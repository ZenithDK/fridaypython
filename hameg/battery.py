#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a crude and simple battery simulator.
It can be charged and discharged, and it also has a cutoff-voltage.
"""

import hameg
import time

TOTAL_CAPACITY = 205 # mAh
MULTIPLIER = 20 # Charging will happen this much (times) faster.
HAMEG_PORT = "/dev/ttyUSB1"
HAMEG_OUTPUT = 1

MAXIMUM_VOLTAGE = 4.2
MINIMUM_VOLTAGE = 2.7
BATTERY_VOLTAGE = 2.9 # volts

psu = hameg.Hameg(HAMEG_PORT)
psu.clear()

def mapValues(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


last_time = time.time()
battery_capacity = mapValues(BATTERY_VOLTAGE, MINIMUM_VOLTAGE, MAXIMUM_VOLTAGE, 0, TOTAL_CAPACITY)

psu.setVoltage(HAMEG_OUTPUT, BATTERY_VOLTAGE)
psu.setCurrent(HAMEG_OUTPUT, 0.5)

while True:
    current = (psu.getMeasuredCurrent(HAMEG_OUTPUT)*1000)*MULTIPLIER # converted to mA
    current_time = time.time()
    battery_capacity = battery_capacity - (current / ((current_time-last_time)) / 3600)
    battery_voltage = mapValues(battery_capacity, 0, TOTAL_CAPACITY, MINIMUM_VOLTAGE, MAXIMUM_VOLTAGE)
    psu.setVoltage(HAMEG_OUTPUT, min(battery_voltage, MAXIMUM_VOLTAGE)) # Make sure we don't go over voltage.
    print "Voltage: %0.2fV (prog.: %0.2fV)\tCurrent: %0.3fA (prog.: %0.2fA, sim.: %0.2fA)\tSim-Cap: %dmAh"%(
            psu.getMeasuredVoltage(HAMEG_OUTPUT),
            psu.getVoltage(HAMEG_OUTPUT),
            psu.getMeasuredCurrent(HAMEG_OUTPUT),
            psu.getCurrent(HAMEG_OUTPUT),
            current/1000,
            battery_capacity
            )
    if battery_voltage < MINIMUM_VOLTAGE:
        psu.setOutputState(False) # Cutoff voltage
    else:
        psu.setOutputState(True)
    last_time = current_time
    time.sleep(1)
