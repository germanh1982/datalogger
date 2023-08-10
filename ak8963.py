from struct import unpack
from enum import Enum
import ak8963regs as akr
from time import time

class AK8963:
    SCALE_FACTOR = 0.6 # uT / LSB

    def _hw_initialize(self):
        self._writereg(akr.CNTL1, 1 << 4 | 6 << 0)
        self._readreg(akr.ST2)

    def _writereg(self, reg, value):
        self._bus.write_i2c_block_data(self._devaddr, reg, [value])

    def _readreg(self, reg):
        value = self._bus.read_i2c_block_data(self._devaddr, reg, 1)
        return value[0]

    def __init__(self, bus, devaddr):
        self._bus = bus
        self._devaddr = devaddr
        self._hw_initialize()

    def read_all(self):
        ts = time()
        data = self._bus.read_i2c_block_data(self._devaddr, akr.HX, 7)
        hx, hy, hz, status = unpack('<hhhB', bytes(data))
        hx *= self.SCALE_FACTOR
        hy *= self.SCALE_FACTOR
        hz *= self.SCALE_FACTOR
        return (ts, (hx, hy, hz), status >> akr.HOFL & 1 == 1)

