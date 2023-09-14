from struct import unpack
from enum import Enum
import mpu9250regs as mpuregs
from time import time

class AccelFSV:
    @classmethod
    def from_value(cls, value):
        for subc in cls.__subclasses__():
            if subc.REGVALUE == value:
                return subc
        raise ValueError(value)

class AccelFSV2G(AccelFSV):
    REGVALUE = 0
    SCALE_FACTOR = 2.0 / 32768

class AccelFSV4G(AccelFSV):
    REGVALUE = 1
    SCALE_FACTOR = 4.0 / 32768

class AccelFSV8G(AccelFSV):
    REGVALUE = 2
    SCALE_FACTOR = 8.0 / 32768

class AccelFSV16G(AccelFSV):
    REGVALUE = 3
    SCALE_FACTOR = 16.0 / 32768

class GyroFSV:
    @classmethod
    def from_value(cls, value):
        for subc in cls.__subclasses__():
            if subc.REGVALUE == value:
                return subc
        raise ValueError(value)

class GyroFSV250DPS(GyroFSV):
    REGVALUE = 0
    SCALE_FACTOR = 250.0 / 32768

class GyroFSV500DPS(GyroFSV):
    REGVALUE = 1
    SCALE_FACTOR = 500.0 / 32768

class GyroFSV1000DPS(GyroFSV):
    REGVALUE = 2
    SCALE_FACTOR = 1000.0 / 32768

class GyroFSV2000DPS(GyroFSV):
    REGVALUE = 3
    SCALE_FACTOR = 2000.0 / 32768

class MPU9250:
    # registers
    def _hw_initialize(self):
        # hard reset
        self._writereg(mpuregs.PWR_MGMT_1, 1 << mpuregs.H_RESET)
        # i2c passthrough for magnetometer to host direct communication
        self._writereg(mpuregs.USER_CTRL, 1 << mpuregs.I2C_MST_EN)
        self._writereg(mpuregs.INT_PIN_CFG, 1 << mpuregs.BYPASS_EN)

    def _writereg(self, reg, value):
        self._bus.write_i2c_block_data(self._devaddr, reg, [value])

    def _readreg(self, reg):
        value = self._bus.read_i2c_block_data(self._devaddr, reg, 1)
        return value[0]

    def __init__(self, bus, devaddr = 0x68, afsv=AccelFSV16G(), gfsv=GyroFSV2000DPS()):
        self._bus = bus
        self._devaddr = devaddr
        self._hw_initialize()

        self.afsv = afsv
        self.gfsv = gfsv

    def read_all(self):
        ts = time()
        data = self._bus.read_i2c_block_data(self._devaddr, mpuregs.ACCEL_XOUT, 14)
        ax, ay, az, temp, gx, gy, gz = unpack('>hhhhhhh', bytes(data))
        ax *= self._afsv.SCALE_FACTOR
        ay *= self._afsv.SCALE_FACTOR
        az *= self._afsv.SCALE_FACTOR
        gx *= self._gfsv.SCALE_FACTOR
        gy *= self._gfsv.SCALE_FACTOR
        gz *= self._gfsv.SCALE_FACTOR
        temp = temp / 321.0 + 21
        return (ts, ax, ay, az, gx, gy, gz, temp)

    @property
    def afsv(self):
        regvalue = self._readreg(mpuregs.ACCEL_CONFIG)
        return AccelFSV.from_value(regvalue >> 3 & 3)

    @afsv.setter
    def afsv(self, sens):
        assert isinstance(sens, AccelFSV)
        reg = self._readreg(mpuregs.ACCEL_CONFIG)
        self._writereg(mpuregs.ACCEL_CONFIG, reg & ~0x18 | sens.REGVALUE << 3)
        self._afsv = sens

    @property
    def gfsv(self):
        regvalue = self._readreg(mpuregs.GYRO_CONFIG)
        return GyroFSV.from_value(regvalue >> 3 & 3)

    @gfsv.setter
    def gfsv(self, sens):
        assert isinstance(sens, GyroFSV)
        reg = self._readreg(mpuregs.GYRO_CONFIG)
        self._writereg(mpuregs.GYRO_CONFIG, reg & ~0x18 | sens.REGVALUE << 3)
        self._gfsv = sens
