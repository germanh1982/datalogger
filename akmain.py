from smbus import SMBus
import ak8963 as ak
from time import sleep, monotonic

bus = SMBus(1)
dev = ak.AK8963(bus, 0x0c)

while True:
    print(dev.read_all())
    sleep(0.02)
print(end - start)
 
