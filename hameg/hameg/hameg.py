#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial

class HamegPort(serial.Serial):
    def __init__(self, portname, baudrate=9600, auto_connect=True):
        super(HamegPort, self).__init__(portname, baudrate=baudrate)

    def readline(self):
        input_buffer = bytearray()
        while True:
            input_byte = self.read(1)
            # It's probably best to follow convention and append the \r
            input_buffer.append(input_byte)
            if input_byte == "\r":
                return input_buffer


class Hameg:
    def __init__(self, portname, baudrate=9600, auto_connect=True):
        self.serialPort = HamegPort(portname, baudrate=baudrate)
        if auto_connect:
            self.connect()

    def connect(self):
        while self.serialPort.inWaiting():
            self.serialPort.read()
        self.serialPort.write("MX1\r\n")

    def clear(self):
        self.serialPort.write("CLR\r\n")

    def setOutputState(self, state):
        self.serialPort.write("OP%d\r\n"%state)

    def setVoltage(self, output, value):
        self.serialPort.write("SU%d:%0.3f\r\n"%(output, value))

    def setCurrent(self, output, value):
        self.serialPort.write("SI%d:%0.3f\r\n"%(output, value))

    def getOutputState(self):
        self.serialPort.write("STA\r\n")
        response = self.serialPort.readline()
        return response.strip()[2] == 49 #ASCII 1

    def getVoltage(self, output):
        """
            Returns the programmed voltage, not actual measured voltage.
        """
        self.serialPort.write("RU%d\r\n"%output)
        response = self.serialPort.readline()
        return float(response.strip()[3:-1])

    def getCurrent(self, output):
        """
            Returns the programmed current, not actual measured current.
        """
        self.serialPort.write("RI%d\r\n"%output)
        response = self.serialPort.readline()
        return float(response.strip()[3:-1])

    def getMeasuredVoltage(self, output):
        """
            Returns the actual measured voltage
        """
        self.serialPort.write("MU%d\r\n"%output)
        response = self.serialPort.readline()
        return float(response.strip()[3:-1])

    def getMeasuredCurrent(self, output):
        """
            Returns the actual measured current
        """
        self.serialPort.write("MI:%d\r\n"%output)
        response = self.serialPort.readline()
        return float(response.strip()[3:-1])
