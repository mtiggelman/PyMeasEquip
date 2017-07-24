import serial

# Assumes use of Prologix GPIB-USB serial converter
class E8257D(serial.Serial):
    def __init__(self, port, baud, GPIB, timeout=1):
        super(E8257D, self).__init__(port, baud, timeout = timeout)
        self.GPIB = GPIB

        self.write(b"++mode 1\r\n")
        data = "++addr "+str(GPIB)+"\r\n"
        self.write(bytes(data, 'utf-8'))
        self.write(b":POW:MODE FIX\r\n")
        self.write(b":FREQ:MODE CW\r\n")

    def set_frequency(self, frequency):
        data = ":FREQ " + str(frequency) + "HZ\r\n"
        self.write(bytes(data, 'utf-8'))

    def set_power(self, power):
        data = ":POW " + str(power) + "DBM\r\n"
        self.write(bytes(data, 'utf-8'))

    def enable_rf(self, enable):
        if enable > 0:
            self.write(b":OUTP ON\r\n")
        else:
            self.write(b":OUTP OFF\r\n")
