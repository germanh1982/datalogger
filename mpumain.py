from smbus import SMBus
import mpu9250 as mpu

imu = mpu.MPU9250(SMBus(1), 0x68)

while True:
    print(imu.read_all())
 
