import serial

# Assumes use of Prologix GPIB-USB serial converter
class HP3458A(serial.Serial):
    def __init__(self, port, baud, timeout, GPIB=22):
        super(HP3458A, self).__init__(port, baud, timeout = timeout)
        # Set GPIB connection
        self.setup_connection(GPIB)
        # Set default 10 PLC and 9 digits
        self.setup_measurement(10, 9)

    # read voltage from HP3458A
    def getVoltage (self):
        self.write('++auto 1\r\n')  # Set instrument to TALK
        self.write('READ?\r\n')     # send READ command

        dat_str = self.readline()   # read upto first '/r/n'

        self.write('++auto 0\r\n')  # Set instrument to LISTEN

        return dat_str[0:16]        # strip trailing '/n'

    def getName(self):
        self.write('++auto 1\r\n')  # Set instrument to TALK
        self.write('ID?\r\n')
        dat_str = self.readline()

        return dat_str[0:17]        # strip trailing '/n'

    def getTemp(self):
        self.write('++auto 1\r\n')  # Set instrument to TALK
        self.write('TEMP?\r\n')     # send READ command

        dat_str = self.readline()   # read upto first '/r/n'

        self.write('++auto 0\r\n')  # Set instrument to LISTEN

        return dat_str[0:16]        # strip trailing '/n'

    def setup_connection(self, GPIB):
        # set GPIB address HP3458A (default 22)
        self.write('++addr ' + str(GPIB) + '\r\n')

    # Set measurement settings
    def setup_measurement(self, NPLC, NDIG):
        # Set to DC voltage measurement
        self.write('DCV\r\n')

        # Set power line cycle integration
        self.write('NPLC ' + str(NPLC) + '\r\n')

        # Set number of digits
        self.write('NDIG ' + str(NDIG) + '\r\n')

        # 1 reading
        self.write('NRDGS 1\r\n')
