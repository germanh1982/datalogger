from smbus import SMBus
from struct import unpack
from time import sleep, monotonic
from enum import Enum

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
    SMPLRT_DIV = 25
    CONFIG = 26
    GYRO_CONFIG = 27
    ACCEL_CONFIG = 28
    ACCEL_CONFIG2 = 29
    FIFO_EN = 35
    PWR_MGMT1 = 107
    PWR_MGMT2 = 108
    FIFO_COUNT = 114
    FIFO_RW = 116
    WHO_AM_I = 117

    BULK_READ_BASE = 59
    BULK_READ_SIZE = 14

    def _hw_initialize(self):
        #self._bus.write_i2c_block_data(self._devaddr, SMPLRT_DIV, 
        pass

    def _writereg(self, reg, value):
        self._bus.write_i2c_block_data(self._devaddr, reg, [value])

    def _readreg(self, reg):
        value = self._bus.read_i2c_block_data(self._devaddr, reg, 1)
        return value[0]

    def __init__(self, bus, devaddr):
        self._bus = bus
        self._devaddr = devaddr
        self._hw_initialize()

        self._afsv = self.afsv
        self._gfsv = self.gfsv

    def read_all(self):
        data = self._bus.read_i2c_block_data(self._devaddr, self.BULK_READ_BASE, self.BULK_READ_SIZE)
        ax, ay, az, temp, gx, gy, gz = unpack('>hhhhhhh', bytes(data))

        out = []
        out.append(ax * self._afsv.SCALE_FACTOR)
        out.append(ay * self._afsv.SCALE_FACTOR)
        out.append(az * self._afsv.SCALE_FACTOR)
        out.append(temp / 321.0 + 21)
        out.append(gx * self._gfsv.SCALE_FACTOR)
        out.append(gy * self._gfsv.SCALE_FACTOR)
        out.append(gz * self._gfsv.SCALE_FACTOR)
        return out

    @property
    def afsv(self):
        regvalue = self._readreg(self.ACCEL_CONFIG)
        return AccelFSV.from_value(regvalue >> 3 & 3)

    @afsv.setter
    def afsv(self, sens):
        assert isinstance(sens, AccelFSV)
        reg = self._readreg(self.ACCEL_CONFIG)
        self._writereg(self.ACCEL_CONFIG, reg & ~0x18 | sens.REGVALUE << 3)
        self._afsv = sens

    @property
    def gfsv(self):
        regvalue = self._readreg(self.GYRO_CONFIG)
        return GyroFSV.from_value(regvalue >> 3 & 3)

    @gfsv.setter
    def gfsv(self, sens):
        assert isinstance(sens, GyroFSV)
        reg = self._readreg(self.GYRO_CONFIG)
        self._writereg(self.GYRO_CONFIG, reg & ~0x18 | sens.REGVALUE << 3)
        self._gfsv = sens

bus = SMBus(1)
imu = MPU9250(bus, 0x68)

print(f"Accel sens = {imu.afsv}")
imu.afsv = AccelFSV2G()
print(f"Accel sens = {imu.afsv}")

print(f"Gyro sens = {imu.gfsv}")
imu.gfsv = GyroFSV250DPS()
print(f"Gyro sens = {imu.gfsv}")

while True:
    print(imu.read_all())
    sleep(0.02)
