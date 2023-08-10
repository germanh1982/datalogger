from bmp280 import BMP280
from smbus import SMBus
from time import sleep, monotonic

dev = BMP280(SMBus(1), 0x76)

start = monotonic()
#while True:
for _ in range(1000):
    print(dev.read_all())
    #sleep(0.05)
end = monotonic()
print(end - start)
