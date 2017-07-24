from time import sleep, time
import numpy as np
import ctypes as ct

class SignalHound(object):

    def __init__(self):
        python_bit = ct.sizeof(ct.c_voidp)
        if python_bit == 8:
            self.dll = ct.CDLL('D:/Marijn/hardware_drivers/signalhound/drivers/x64/sa_api.dll')
        else:
            self.dll = ct.CDLL('D:/Marijn/hardware_drivers/signalhound/drivers/x64/sa_api.dll')

        self.cst = saConstants
        self.sts = saStatus

        self.dev_handle = 0
        self.dev_serial = 0
        self.dev_type = 'No device'
        self.dev_open = False
        self.detector = ''
        self.scale = ''
        self.start_frequency = None
        self.stop_frequency = None
        self.center_frequency = None
        self.span = None
        self.ref_level = None
        self.RBW = None
        self.VBW = None
        self.reject = True
        self.units = ''
        self.timebase = ''
        self.mode = 'idle'

    def get_serial_number_list(self):
        # Returns list of the serial numbers of devices connected (upto 8)
        dev_list = (ct.c_int32 * 8)()
        dev_count = ct.c_int32(0)

        err = self.dll.saGetSerialNumberList(dev_list, ct.pointer(dev_count))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saNullPtrErr:
            raise ValueError('Null pointer error!')
        else:
            raise ValueError('Unknown error: %d' %err)

        return np.array(dev_list[:])

    def open_device(self):
        # Opens first device that it detects
        dev_handle_c = ct.c_int32(0)
        err = self.dll.saOpenDevice(ct.pointer(dev_handle_c))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saNullPtrErr:
            raise ValueError('Null pointer error!')
        elif err == self.sts.saDeviceNotFoundErr:
            raise IOError('Could not open device!')
        elif err == self.sts.saInternetErr:
            raise IOError('Could not get calibration files from the server!')
        else:
            raise ValueError('Unknown error: %d' %err)

        self.dev_handle = dev_handle_c.value
        self.dev_open = True
        self.get_serial_number()
        self.get_device_type()

    def open_device_by_serial(self, serial):
        # Opens device by serial number
        dev_handle_c = ct.c_int32(0)
        err = self.dll.saOpenDeviceBySerialNumber(ct.pointer(dev_handle_c), ct.c_int32(serial))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saNullPtrErr:
            raise ValueError('Null pointer error!')
        elif err == self.sts.saDeviceNotFoundErr:
            raise IOError('Could not open device!')
        elif err == self.sts.saInternetErr:
            raise IOError('Could not get calibration files from the server!')
        else:
            raise ValueError('Unknown error: %d' %err)

        self.dev_handle = dev_handle_c.value
        self.dev_open = True
        self.get_serial_number()
        self.get_device_type()

    def close_device(self):
        # Closes connection with device
        err = self.dll.saCloseDevice(ct.c_int32(self.dev_handle))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        else:
            raise ValueError('Unknown error: %d' %err)

        self.dev_handle = 0
        self.dev_serial = 0
        self.dev_type = 'No device'
        self.dev_open = False
        self.detector = ''
        self.scale = ''
        self.start_frequency = None
        self.stop_frequency = None
        self.center_frequency = None
        self.span = None
        self.ref_level = None
        self.RBW = None
        self.VBW = None
        self.reject = None
        self.units = ''
        self.timebase = ''
        self.mode = 'idle'

    def get_serial_number(self):
        # Returns serial number of connected device
        dev_serial_c = ct.c_int32(0)
        err = self.dll.saGetSerialNumber(ct.c_int32(self.dev_handle), ct.pointer(dev_serial_c))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saNullPtrErr:
            raise ValueError('Null pointer error!')
        else:
            raise ValueError('Unknown error: %d' %err)

        self.dev_serial = dev_serial_c.value

    def get_device_type(self):
        # Returns device type of connected device
        dev_type_c = ct.c_uint(0)
        err = self.dll.saGetDeviceType(ct.c_int32(self.dev_handle), ct.pointer(dev_type_c))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saNullPtrErr:
            raise ValueError('Null pointer error!')
        else:
            raise ValueError('Unknown error: %d' %err)

        if dev_type_c.value == self.cst.saDeviceTypeNone:
            self.dev_type = 'No device'
        elif dev_type_c.value == self.cst.saDeviceTypeSA44:
            self.dev_type = 'sa44'
        elif dev_type_c.value == self.cst.saDeviceTypeSA44B:
            self.dev_type = 'sa44B'
        elif dev_type_c.value == self.cst.saDeviceTypeSA124A:
            self.dev_type = 'sa124A'
        elif dev_type_c.value == self.cst.saDeviceTypeSA124B:
            self.dev_type = 'sa124B'
        else:
            raise ValueError('Unknown device!')

    def config_acquisition(self, detector, scale):
        # Sets detector type (min/max or average) and scale (log or lin)
        detector_values = {
            'min-max': ct.c_uint(self.cst.sa_MIN_MAX),
            'average': ct.c_uint(self.cst.sa_AVERAGE)
        }

        scale_values = {
            'log-scale': ct.c_uint(self.cst.sa_LOG_SCALE),
            'lin-scale': ct.c_uint(self.cst.sa_LIN_SCALE),
            'log-full-scale': ct.c_uint(self.cst.sa_LOG_FULL_SCALE),
            'lin-full-scale': ct.c_uint(self.cst.sa_LIN_FULL_SCALE)
        }

        if detector in detector_values:
            detector_c = detector_values[detector]
        else:
            raise ValueError('Invalid detector value! Must be one of: %s' %list(detector_values.keys()))

        if scale in scale_values:
            scale_c = scale_values[scale]
        else:
            raise ValueError('Invalid scale value! Must be one of: %s' %list(scale_values.keys()))

        err = self.dll.saConfigAcquisition(ct.c_int32(self.dev_handle), detector_c, scale_c)

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saInvalidDetectorErr:
            raise ValueError('Detector value not accepted!')
        elif err == self.sts.saInvalidScaleErr:
            raise ValueError('Scale value not accepted!')
        else:
            raise ValueError('Unknown error: %d' %err)

        self.detector = detector
        self.scale = scale

    def config_sweep_by_freq(self, start_frequency, stop_frequency):
        # Sets sweep by start and stop frequency, calculate center and span
        if self.dev_type == self.cst.saDeviceTypeSA44 or self.dev_type == self.cst.saDeviceTypeSA44B:
            if start_frequency < self.cst.sa44_MIN_FREQ:
                raise ValueError('Start frequency has to be equal to or above %dHz' %self.cst.sa44_MIN_FREQ)
            if stop_frequency > self.cst.sa44_MAX_FREQ:
                raise ValueError('Stop frequency has to be equal to or below %dHz' %self.cst.sa44_MAX_FREQ)
        elif self.dev_type == self.cst.saDeviceTypeSA124A or self.dev_type == self.cst.saDeviceTypeSA124B:
            if start_frequency < self.cst.sa124_MIN_FREQ:
                raise ValueError('Start frequency has to be equal to or above %dHz' %self.cst.sa124_MIN_FREQ)
            if stop_frequency > self.cst.sa124_MAX_FREQ:
                raise ValueError('Stop frequency has to be equal to or below %dHz' %self.cst.sa124_MAX_FREQ)

        center_c = ct.c_double((start_frequency+stop_frequency)/2.0)
        span_c = ct.c_double(stop_frequency - start_frequency)

        err = self.dll.saConfigCenterSpan(ct.c_int32(self.dev_handle), center_c, span_c)

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saFrequencyRangeErr:
            ValueError("Calculated start or stop frequencies fall outside of operational frequency range or span < 1Hz!")
        else:
            raise ValueError('Unknown error: %d' %err)

        self.start_frequency = start_frequency
        self.stop_frequency = stop_frequency
        self.center_frequency = center_c.value
        self.span = span_c.value

    def config_sweep_by_span(self, center_frequency, span):
        # Sets sweep by span and center frequency, calculate start and stop
        start_frequency = center_frequency - (span/2.0)
        stop_frequency = center_frequency + (span/2.0)

        if self.dev_type == self.cst.saDeviceTypeSA44 or self.dev_type == self.cst.saDeviceTypeSA44B:
            if start_frequency < self.cst.sa44_MIN_FREQ:
                raise ValueError('Start frequency has to be equal to or above %dHz' %self.cst.sa44_MIN_FREQ)
            if stop_frequency > self.cst.sa44_MAX_FREQ:
                raise ValueError('Stop frequency has to be equal to or below %dHz' %self.cst.sa44_MAX_FREQ)
        elif self.dev_type == self.cst.saDeviceTypeSA124A or self.dev_type == self.cst.saDeviceTypeSA124B:
            if start_frequency < self.cst.sa124_MIN_FREQ:
                raise ValueError('Start frequency has to be equal to or above %dHz' %self.cst.sa124_MIN_FREQ)
            if stop_frequency > self.cst.sa124_MAX_FREQ:
                raise ValueError('Stop frequency has to be equal to or below %dHz' %self.cst.sa124_MAX_FREQ)

        center_c = ct.c_double(center_frequency)
        span_c = ct.c_double(span)

        err = self.dll.saConfigCenterSpan(ct.c_int32(self.dev_handle), center_c, span_c)

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saFrequencyRangeErr:
            ValueError("Calculated start or stop frequencies fall outside of operational frequency range or span < 1Hz!")
        else:
            raise ValueError('Unknown error: %d' %err)

        self.start_frequency = start_frequency
        self.stop_frequency = stop_frequency
        self.center_frequency = center_frequency
        self.span = span

    def config_ref_level(self, level):
        # Sets the reference level in dBm
        level_c = ct.c_double(level)
        err = self.dll.saConfigLevel(ct.c_int32(self.dev_handle), level_c)

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saInvalidParameterErr:
            ValueError("Value for units did not match any known value!")
        else:
            raise ValueError('Unknown error: %d' %err)

        self.ref_level = level

    def config_BW(self, rbw, vbw, reject=True):
        # Sets RBW and VBW, and enable/disable image reject
        if rbw < self.cst.sa_MIN_RBW or rbw > self.cst.sa_MAX_RBW:
            raise ValueError('RBW has to be between %dHz and %dHz!' %(self.cst.sa_MIN_RBW, self.cst.sa_MAX_RBW))
        if vbw > rbw:
            raise ValueError('VBW has to be equal to or smaller than RBW!')

        rbw_c = ct.c_double(rbw)
        vbw_c = ct.c_double(vbw)
        reject_c = ct.c_bool(reject)

        err = self.dll.saConfigSweepCoupling(ct.c_int32(self.dev_handle), rbw_c, vbw_c, reject_c)

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saBandwidthErr:
            ValueError("RBW or VBW outside possible range or VBW > RBW!")
        else:
            raise ValueError('Unknown error: %d' %err)

        self.RBW = rbw
        self.VBW = vbw

    def config_proc_units(self, units):
        # Sets processing units: log, volt, power, bypass
        unit_values = {
            'log-units': ct.c_uint(self.cst.sa_LOG_UNITS),
            'volt-units': ct.c_uint(self.cst.sa_VOLT_UNITS),
            'power-units': ct.c_uint(self.cst.sa_POWER_UNITS),
            'bypass': ct.c_uint(self.cst.sa_BYPASS)
        }

        if units in unit_values:
            units_c = unit_values[units]
        else:
            raise ValueError('Invalid detector value! Must be one of: %s' %list(unit_values.keys()))

        err = self.dll.saConfigProcUnits(ct.c_int32(self.dev_handle), units_c)

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise ValueError('Setting provided is not supported on device specified!')
        elif err == self.sts.saExternalReferenceNotFound:
            raise ValueError('Unable to find an external reference on the BNC port!')
        else:
            raise ValueError('Unknown error: %d' %err)

    def set_timebase(self, timebase):
        # Sets reference external/internal (+ output)
        timebase_values = {
            'internal-out': ct.c_uint(self.cst.sa_REF_INTERNAL_OUT),
            'external-in': ct.c_uint(self.cst.sa_REF_EXTERNAL_IN)
        }

        if timebase in timebase_values:
            timebase_c = timebase_values[timebase]
        else:
            raise ValueError('Invalid detector value! Must be one of: %s' %list(timebase_values.keys()))

        err = self.dll.saSetTimebase(ct.c_int32(self.dev_handle), timebase_c)

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saInvalidDeviceErr:
            raise ValueError('Setting provided is not supported on device specified!')
        elif err == self.sts.saExternalReferenceNotFound:
            raise ValueError('Unable to find an external reference on the BNC port!')
        else:
            raise ValueError('Unknown error: %d' %err)

        self.timebase = timebase

    def initiate(self, mode):
        mode_values = {
            'idle': ct.c_uint(self.cst.sa_IDLE),
            'sweeping': ct.c_uint(self.cst.sa_SWEEPING)
            # Other modes not implemented yet
        }

        if mode in mode_values:
            mode_c = mode_values[mode]
        else:
            raise ValueError('Invalid mode value! Must be one of: %s' %list(mode_values.keys()))

        err = self.dll.saInitiate(ct.c_int32(self.dev_handle), mode_c, ct.c_uint(0))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saInvalidDeviceErr:
            raise ValueError('Setting provided is not supported on device specified!')
        elif err == self.sts.saInvalidParameterErr:
            raise ValueError('Value for mode did not match any known value!')
        elif err == self.sts.saParameterClamped:
            print("Warning! One or more config values were clamped in order to configure device into the mode specified!")
        elif err == self.sts.saBandwidthClamped:
            print("Warning! The RBW or VBW was limited based on supplied span and/or hardware limitations!")
        else:
            raise ValueError('Unknown error: %d' %err)

        self.mode = mode

    def abort(self):
        # Aborts device operation mode
        err = self.dll.saAbort(ct.c_int32(self.dev_handle))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        else:
            raise ValueError('Unknown error: %d' %err)

        self.mode = 'idle'

    def query_sweep_info(self):
        # Get information about the sweep from the device
        sweepLength = ct.c_int(0)
        startFreq = ct.c_double(0)
        binSize = ct.c_double(0)

        err = self.dll.saQuerySweepInfo(ct.c_int32(self.dev_handle), ct.pointer(sweepLength), ct.pointer(startFreq), ct.pointer(binSize))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saNullPtrErr:
            raise ValueError('Null pointer error!')
        elif err == self.sts.saNotConfiguredErr:
            raise IOError('Device not configured for sweeps!')
        else:
            raise ValueError('Unknown error: %d' %err)

        return [sweepLength.value, startFreq.value, binSize.value]

    def sweep(self, no_avg=1):
        # Does sweep 'no_avg' times and averages, return array with Data
        sweepLen, startFreq, binSize = self.query_sweep_info()
        end_freq = startFreq + binSize*(sweepLen-1)
        freq_points = np.linspace(startFreq, end_freq, sweepLen)

        minarr = (ct.c_float * sweepLen)()
        maxarr = (ct.c_float * sweepLen)()

        err = self.dll.saGetSweep_32f(ct.c_int32(self.dev_handle), minarr, maxarr)

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saNullPtrErr:
            raise ValueError('Null pointer error!')
        elif err == self.sts.saNotConfiguredErr:
            raise IOError('Device is in idle mode!')
        elif err == self.sts.saInvalidModeErr:
            raise IOError('Device not configured for sweeps!')
        elif err == self.sts.saCompressionWarning:
            print("Warning! ADC detected clipping of input signal! Change reference value or lower input!")
        elif err == self.sts.saUSBCommErr:
            raise IOError('Device connection issues were present in the acquisition of this sweep!')
        else:
            raise ValueError('Unknown error: %d' %err)

        datamin = np.array(minarr[:])
        datamax = np.array(maxarr[:])

        return np.array([freq_points, datamin, datamax])

    def get_temperature(self):
        # Returns device temperature, device cannot be active: call abort first
        if self.mode != 'idle':
            print("Not possible to get temperature if device is not idle! Use 'abort' first!")
            return

        temperature = ct.c_float(0)
        err = self.dll.saQueryTemperature(ct.c_int32(self.dev_handle), ct.pointer(temperature))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saNullPtrErr:
            raise ValueError('Null pointer error!')
        else:
            raise ValueError('Unknown error: %d' %err)

        return temperature.value

    def get_system_voltage(self):
        # Returns system voltage
        voltage = ct.c_float(0)
        err = self.dll.saQueryDiagnostics(ct.c_int32(self.dev_handle), ct.pointer(voltage))

        if err == self.sts.saNoError:
            pass
        elif err == self.sts.saDeviceNotOpenErr:
            raise IOError('Device specified is not open!')
        elif err == self.sts.saNullPtrErr:
            raise ValueError('Null pointer error!')
        elif err == self.sts.saDeviceNotIdleErr:
            print('Device is currently active! Call abort before trying again.')
        else:
            raise ValueError('Unknown error: %d' %err)

        return voltage.value

class saStatus:
    saUnknownErr = -666

	# Setting specific error codes
    saFrequencyRangeErr = -99
    saInvalidDetectorErr = -95
    saInvalidScaleErr = -94
    saBandwidthErr = -91
    saExternalReferenceNotFound = -89

	# Device-specific errors
    saOvenColdErr = -20

	# Data errors
    saInternetErr = -12
    saUSBCommErr = -11

	# General configuration errors
    saTrackingGeneratorNotFound = -10
    saDeviceNotIdleErr = -9
    saDeviceNotFoundErr = -8
    saInvalidModeErr = -7
    saNotConfiguredErr = -6
    saTooManyDevicesErr = -5
    saInvalidParameterErr = -4
    saDeviceNotOpenErr = -3
    saInvalidDeviceErr = -2
    saNullPtrErr = -1

	# No Error
    saNoError = 0

	# Warnings
    saNoCorrections = 1
    saCompressionWarning = 2
    saParameterClamped = 3
    saBandwidthClamped = 4

class saConstants:
    SA_MAX_DEVICES = 8

    saDeviceTypeNone = 0
    saDeviceTypeSA44 = 1
    saDeviceTypeSA44B = 2
    saDeviceTypeSA124A = 3
    saDeviceTypeSA124B = 4

    sa44_MIN_FREQ = 1.0
    sa124_MIN_FREQ = 100.0e3
    sa44_MAX_FREQ = 4.4e9
    sa124_MAX_FREQ = 12.4e9
    sa_MIN_SPAN = 1.0
    sa_MAX_REF = 20
    sa_MAX_ATTEN = 3
    sa_MAX_GAIN = 2
    sa_MIN_RBW = 0.1
    sa_MAX_RBW = 6.0e6
    sa_MIN_RT_RBW = 100.0
    sa_MAX_RT_RBW = 10000.0
    sa_MIN_IQ_BANDWIDTH = 100.0
    sa_MAX_IQ_DECIMATION = 128

    sa_IQ_SAMPLE_RATE = 486111.111

    sa_IDLE = -1
    sa_SWEEPING = 0x0
    sa_REAL_TIME = 0x1
    sa_IQ = 0x2
    sa_AUDIO = 0x3
    sa_TG_SWEEP = 0x4

    sa_MIN_MAX = 0x0
    sa_AVERAGE = 0x1

    sa_LOG_SCALE = 0x0
    sa_LIN_SCALE = 0x1
    sa_LOG_FULL_SCALE = 0x2
    sa_LIN_FULL_SCALE = 0x3

    sa_AUTO_ATTEN = -1
    sa_AUTO_GAIN = -1

    sa_LOG_UNITS = 0x0
    sa_VOLT_UNITS = 0x1
    sa_POWER_UNITS = 0x2
    sa_BYPASS = 0x3

    sa_AUDIO_AM = 0x0
    sa_AUDIO_FM = 0x1
    sa_AUDIO_USB = 0x2
    sa_AUDIO_LSB = 0x3
    sa_AUDIO_CW = 0x4

    TG_THRU_0DB = 0x1
    TG_THRU_20DB = 0x2

    sa_REF_INTERNAL_OUT = 0x01
    sa_REF_EXTERNAL_IN = 0x02
