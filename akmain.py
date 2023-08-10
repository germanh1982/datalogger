from smbus import SMBus
import ak8963 as ak

dev = ak.AK8963(SMBus(1), 0x0c)

while True:
    print(dev.read_all())
 
