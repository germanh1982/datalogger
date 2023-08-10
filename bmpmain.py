from bmp280 import BMP280
from smbus import SMBus
from time import sleep

dev = BMP280(SMBus(1), 0x76)

while True:
    ts, temp, pres = dev.read_all()
    print(pres)
    sleep(0.05)
