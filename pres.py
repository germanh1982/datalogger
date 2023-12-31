#!/usr/bin/python3
from smbus import SMBus
from bmp280 import BMP280
import paho.mqtt.client as mqttc
from json import dumps
from time import sleep, monotonic
from argparse import ArgumentParser
import logging

def main():
    dev = BMP280(SMBus(args.bus), args.i2caddr)
    while True:
        start = monotonic()
        count = 0
        while monotonic() - start < 1:
            ts, temp, pres = dev.read_all()
            client.publish(args.topic, dumps({'ts': ts, 'temp': temp, 'pres': pres}))
            count += 1
            sleep(args.delay)
        log.info(f"samples/sec: {count}")

if __name__ == "__main__":
    p = ArgumentParser(description="Temperature/atmospheric pressure sensor poller and MQTT publisher.")
    p.add_argument('-b', '--bus', type=int, default=1, help="I2C bus where the sensor is connected.")
    p.add_argument('-a', '--i2caddr', type=int, default=0x76, help="Sensor I2C address.")
    p.add_argument('-t', '--topic', default='pres', help="MQTT topic used to publish samples.")
    p.add_argument('-d', '--delay', type=float, default=0.1, help="Minimum delay between samples [ms].")
    p.add_argument('-l', '--loglevel', choices=['debug', 'info', 'warning', 'error', 'critical', 'none'], default='info')
    args = p.parse_args()

    logging.basicConfig(level=args.loglevel.upper())
    log = logging.getLogger()

    client = mqttc.Client()
    client.connect('localhost')
    client.loop_start()

    try:
        main()
    except KeyboardInterrupt:
        client.loop_stop()
