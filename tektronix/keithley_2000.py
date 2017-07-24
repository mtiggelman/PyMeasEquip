import serial
import numpy as np
from time import sleep, time

class keithley_2000(serial.Serial):
    def __init__(self, port, baud, timeout=1):
        super(keithley_2000, self).__init__(port, baud, timeout = timeout)
        print(self.get_ID())

    def get_ID(self):
        self.write(b'*IDN?\r\n')
        return self.readline()

    def get_meas(self):
        self.write(b':READ?\r\n')
        return float(self.readline())
