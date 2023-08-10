from smbus import SMBus
import mpu9250 as mpu
from time import sleep, monotonic

bus = SMBus(1)
imu = mpu.MPU9250(bus, 0x68)

print(f"Accel sens = {imu.afsv}")
imu.afsv = mpu.AccelFSV4G()
print(f"Accel sens = {imu.afsv}")

print(f"Gyro sens = {imu.gfsv}")
imu.gfsv = mpu.GyroFSV1000DPS()
print(f"Gyro sens = {imu.gfsv}")

for _ in range(100):
#while True:
    print(imu.read_all())
    #sleep(0.02)
 
