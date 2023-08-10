#!/usr/bin/python3
from smbus import SMBus
import mpu9250 as mpu
import paho.mqtt.client as mqttc
from json import dumps
from time import sleep, monotonic
from argparse import ArgumentParser

def main():
    dev = mpu.MPU9250(SMBus(args.bus), args.i2caddr)
    while True:
        start = monotonic()
        count = 0
        while monotonic() - start < 1:
            ts, ax, ay, az, temp, gx, gy, gz = dev.read_all()
            client.publish(args.topic, dumps({'ts': ts, 'acc': [ax, ay, az], 'gyr': [gx, gy, gz]}))
            count += 1
            sleep(args.delay)
        print(f"samples/sec = {count}")

if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument('-b', '--bus', type=int, default=1, help="I2C bus where the sensor is connected.")
    p.add_argument('-a', '--i2caddr', type=int, default=12, help="Sensor I2C address.")
    p.add_argument('-t', '--topic', default='magn', help="MQTT topic used to publish samples.")
    p.add_argument('-d', '--delay', type=int, default=0, help="Minimum delay between samples [ms].")
    args = p.parse_args()

    client = mqttc.Client()
    client.connect('localhost')
    client.loop_start()

    try:
        main()
    except KeyboardInterrupt:
        client.loop_stop()
