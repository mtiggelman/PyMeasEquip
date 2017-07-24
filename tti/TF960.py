import serial

class TF960(serial.Serial):
    def __init__(self, port, baud, timeout=0.5):
        super(TF960, self).__init__(port, baud, timeout = timeout)
        self.measurement_time = 0

    def get_ID(self):
        self.write(b'*IDN?\r\n')
        return self.readline().decode()

    def set_function(self, function):
        unit_values = {
            'B-period': b'F0\r\n',
            'A-period': b'F1\r\n',
            'A-frequency': b'F2\r\n',
            'B-frequency': b'F3\r\n',
            'Ratio-B:A': b'F4\r\n',
            'A-width-high': b'F5\r\n',
            'A-width-low': b'F6\r\n',
            'A-count': b'F7\r\n',
            'A-ratio-H:L': b'F8\r\n',
            'A-duty': b'F9\r\n',
            'C-frequency': b'FC\r\n',
            'C-period': b'FD\r\n'
        }

        if function in unit_values:
            value = unit_values[function]
        else:
            raise ValueError('Invalid function value! Must be one of: %s' %list(unit_values.keys()))

        self.write(value)
        self.stop_measurement()

    def set_inputA_coupling(self, coupling):
        unit_values = {
            'AC': b'AC\r\n',
            'DC': b'DC\r\n'
        }

        if coupling in unit_values:
            value = unit_values[coupling]
        else:
            raise ValueError('Invalid coupling value! Must be one of: %s' %list(unit_values.keys()))

        self.write(value)

    def set_inputA_impedance(self, impedance):
        unit_values = {
            '1M': b'Z1\r\n',
            '50': b'Z5\r\n'
        }

        if impedance in unit_values:
            value = unit_values[impedance]
        else:
            raise ValueError('Invalid impedance value! Must be one of: %s' %list(unit_values.keys()))

        self.write(value)

    def set_inputA_attenuation(self, attenuation):
        unit_values = {
            '1:1': b'A1\r\n',
            '5:1': b'A5\r\n'
        }

        if attenuation in unit_values:
            value = unit_values[attenuation]
        else:
            raise ValueError('Invalid attenuation value! Must be one of: %s' %list(unit_values.keys()))

        self.write(value)

    def set_inputA_edge(self, edge):
        unit_values = {
            'rising': b'ER\r\n',
            'falling': b'EF\r\n'
        }

        if edge in unit_values:
            value = unit_values[edge]
        else:
            raise ValueError('Invalid edge value! Must be one of: %s' %list(unit_values.keys()))

        self.write(value)

    def set_inputA_filter(self, state):
        # Turn filter on if state != 0 or False
        if state:
            self.write(b'FI\r\n')
        else:
            self.write(b'FO\r\n')

    def set_DC_threshold(self, value):
        if value > -300 and value < 2100:
            value = bytes(value,'utf-8')
        else:
            raise ValueError('Invalid threshold value! Must be between -300 and 2100 mV')

        self.write(b'TT'+value+'\r\n')

    def start_measurement(self, measurement_time):
        unit_values = {
            0.3: b'M1\r\n',
            1: b'M2\r\n',
            10: b'M3\r\n',
            100: b'M4\r\n'
        }

        if measurement_time in unit_values:
            value = unit_values[measurement_time]
            self.measurement_time = measurement_time
        else:
            raise ValueError('Invalid measurement time! Must be one of: %s' %list(unit_values.keys()))

        self.write(value)
        self.write(b'E?\r\n')

    def reset_measurement(self):
        self.write(b'R\r\n')

    def get_measurement(self):
        self.flushInput()

        value = self.readline()
        while len(value) == 0:
            value = self.readline()

        value = value.decode()
        num = float(value[0:11])
        exp = int(value[13:14])
        return num * 10**exp

    def stop_measurement(self):
        self.write(b'STOP\r\n')
        self.flushInput()
