from struct import unpack
from time import time
import bmp280regs as bmr

class BMP280:
    def _hw_initialize(self):
        self._writereg(bmr.CTRL_MEAS, 1 << bmr.OSRS_T | 1 << bmr.OSRS_P | 3 << bmr.MODE)

    def _writereg(self, reg, value):
        self._bus.write_i2c_block_data(self._devaddr, reg, [value])

    def _readreg(self, reg):
        value = self._bus.read_i2c_block_data(self._devaddr, reg, 1)
        return value[0]

    def __init__(self, bus, devaddr):
        self._bus = bus
        self._devaddr = devaddr
        self._hw_initialize()

        raw_calib = self._bus.read_i2c_block_data(self._devaddr, bmr.CALIB, 24)
        calib_values = unpack('<H2hH8h', bytes(raw_calib))
        calib_keys = [
            'dig_T1', 'dig_T2', 'dig_T3', 'dig_P1', 'dig_P2', 'dig_P3',
            'dig_P4', 'dig_P5', 'dig_P6', 'dig_P7', 'dig_P8', 'dig_P9'
        ]
        for k, v in zip(calib_keys, calib_values):
            setattr(self, k, v)

    def _calc(self, raw_temp, raw_pres):
        # temperature calculation
        t_fine = self.dig_T2 * (raw_temp / 16384.0 - self.dig_T1 / 1024.0) + self.dig_T3 * (raw_temp / 131072.0 - self.dig_T1 / 8192.0)**2
        t = t_fine / 5120.0

        # pressure calculation
        v1 = t_fine / 2.0 - 64000.0
        v2 = v1**2 * self.dig_P6 / 32768.0
        v2 += v1 * self.dig_P5 * 2.0
        v2 = v2 / 4.0 + self.dig_P4 * 65536.0
        v1 = (self.dig_P3 * v1**2 / 524288.0 + self.dig_P2 * v1) / 524288.0
        v1 = (1.0 + v1 / 32768.0) * self.dig_P1

        if v1 == 0:
            return None

        p = 1048576.0 - raw_pres
        p = (p - (v2 / 4096.0)) * 6250.0 / v1
        v1 = self.dig_P9 * p**2 / 2147483648.0
        v2 = p * self.dig_P8 / 32768.0
        p += (v1 + v2 + self.dig_P7) / 16.0

        return (t, p)

    def read_all(self):
        ts = time()
        data = self._bus.read_i2c_block_data(self._devaddr, bmr.PRESS, 6)
        temp, pres = self._calc(
            int.from_bytes(data[3:6], 'big') >> 4,
            int.from_bytes(data[0:3], 'big') >> 4 
        )
        return (ts, temp, pres)
