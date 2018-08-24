import serial
import numpy as np
from time import sleep, time

class keithley_2000(serial.Serial):
    def __init__(self, port, baud, timeout=1):
        super(keithley_2000, self).__init__(port, baud, timeout = timeout)
        print(self.get_ID())

        self.set_function('voltage:dc')
        self.set_sample_count(1)
        self.set_nplc(1)

    def get_ID(self):
        self.write(b'*IDN?\r\n')
        return self.readline()

    def set_function(self, function):
        possible_values = [ 'current:ac', 'current:dc', 'voltage:ac', 'voltage:dc',
                            'resistance', 'fresistance', 'period', 'frequency',
                            'temperature', 'diode', 'continuity']
        if function not in possible_values:
            raise ValueError('Value {} does not exist. Possible values are: {}'.format(function, possible_values))

        self.write(b'configure:' + function.encode() + b'\r\n')

        self.function = function

    def set_sample_count(self, count):
        if not isinstance(count, int):
            raise ValueError('Count must be an integer')
        if count < 1 or count > 1024:
            raise ValueError('Value {} not allowed: 1 <= count <= 1024'.format(count))

        self.write(b'sample:count ' + str(count).encode() + b'\r\n')

        self.count = count

    def set_nplc(self, nplc):
        possible_functions = [  'current:ac', 'current:dc', 'voltage:ac', 'voltage:dc',
                                'resistance', 'fresistance', 'temperature']
        if not isinstance(nplc, int):
            raise ValueError('Count must be an integer')
        if nplc < 0.01 or nplc > 10.0:
            raise ValueError('Value {} not allowed: 0.01 <= nplc <= 10.0'.format(nplc))
        if self.function not in possible_functions:
            raise ValueError('The current function {} does not allow nplc to be set'.format(self.function))

        self.write(b'sense:' + self.function.encode() + b':nplcycles ' +str(nplc).encode() + b'\r\n')

        self.nplc = nplc

    def get_meas(self):
        self.write(b':READ?\r\n')
        return float(self.readline())
