#!/usr/bin/python3
from smbus import SMBus
import mpu9250 as mpu
from argparse import ArgumentParser

def main():
    dev = mpu.MPU9250(SMBus(args.bus), args.i2caddr)

if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument('-b', '--bus', type=int, default=1, help="I2C bus where the sensor is connected.")
    p.add_argument('-a', '--i2caddr', type=int, default=0x68, help="Sensor I2C address.")
    args = p.parse_args()

    main()
