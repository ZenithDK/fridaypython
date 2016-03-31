#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hameg

if __name__ == "__main__":
    h = hameg.Hameg("/dev/ttyUSB1") # Set to COMXX on Windows (e.g. COM1, COM2)

    # Clear everything and make sure the output is disabled.
    h.clear()

    # Do a voltage run on both outputs
    for output in [1, 2]:
        voltage = 0.0
        while voltage <= 5.0:
            h.setVoltage(output, voltage)
            voltage = voltage + 0.01

    # Do a current run on both outputs
    for output in [1, 2]:
        current = 0.0
        while current <= 1.0:
            h.setCurrent(output, current)
            current = current + 0.01


