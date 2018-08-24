import serial

# Assumes use of Prologix GPIB-USB serial converter
class HP3458A(serial.Serial):
    def __init__(self, port, baud, timeout, GPIB=22):
        super(HP3458A, self).__init__(port, baud, timeout = timeout)

        self.vrange = None
        self.nplc = None
        self.ndig = None
        self.address = None

        # Set GPIB connection
        self.setup_connection(GPIB)
        # Setup basic configuration
        self.basic_configuration()
        print(self.get_ID())

    def get_ID(self):
        self.write(b'ID?\r\n')
        return self.readline()

    def start_meas(self):
        self.write(b'TARM SGL,1\r\n')

    def get_result(self):
        return self.readline()

    def setup_connection(self, GPIB):
        if not isinstance(GPIB, int):
            raise ValueError('GPIB must be an integer')
        if GPIB < 0 or GPIB > 30:
            raise ValueError('Value {} not allowed: 0 <= nplc <= 30')

        # Set Prologix to Controller and write/listen mode
        self.write(b'++mode 1\r\n')
        self.write(b'++auto 1\r\n')
        # Set the adress of the device to talk to
        self.write(b'++addr ' + str(GPIB).encode() + b'\r\n')

        self.address = GPIB

    def set_nplc(self, nplc):
        if not isinstance(nplc, int):
            raise ValueError('nplc must be an integer')
        if nplc < 0:
            raise ValueError('Value {} not allowed: nplc > 0'.format(nplc))

        self.write(b'NPLC ' + str(nplc).encode() + b'\r\n')
        self.nplc = nplc

    def set_ndig(self, ndig):
        if not isinstance(ndig, int):
            raise ValueError('ndig must be an integer')
        if ndig < 3 or ndig > 8:
            raise ValueError('Value {} not allowed: 3 <= nplc <= 8'.format(ndig))

        self.write(b'NDIG ' + str(ndig).encode() + b'\r\n')
        self.ndig = ndig

    def set_range(self, vrange):
        self.write(b'RANGE ' + str(vrange).encode() + b'\r\n')
        self.vrange = vrange

    def basic_configuration(self, vrange = 10, nplc = 10, ndig = 8):
        self.write(b'PRESET NORM\r\n') # Load normal preset
        self.write(b'OFORMAT ASCII\r\n') # Output ascii string
        self.write(b'DCV ' + str(vrange).encode() + b'\r\n') # Set DC + vrange
        self.write(b'TARM HOLD\r\n') # Trigger arm hold
        self.write(b'TRIG AUTO\r\n') # Trigger auto
        self.write(b'NPLC ' + str(nplc).encode() + b'\r\n') # Set nplc
        self.write(b'NRDGS 1,AUTO\r\n') # No. of readings to 1
        self.write(b'MEM OFF\r\n') # Turn memory off
        self.write(b'END ALWAYS\r\n')
        self.write(b'NDIG ' + str(ndig).encode() + b'\r\n') # No. of digits

        self.vrange = vrange
        self.nplc = nplc
        self.ndig = ndig
