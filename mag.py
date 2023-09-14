#!/usr/bin/python3
from smbus import SMBus
from ak8963 import AK8963
import paho.mqtt.client as mqttc
from json import dumps
from time import sleep, monotonic
from argparse import ArgumentParser
import logging

def main():
    dev = AK8963(SMBus(args.bus), args.i2caddr)
    while True:
        start = monotonic()
        count = 0
        while monotonic() - start < 1:
            ts, hx, hy, hz, ovf = dev.read_all()
            client.publish(args.topic, dumps({'ts': ts, 'mag': [hx, hy, hz], 'ov': ovf}))
            count += 1
            sleep(args.delay)
        log.info(f"samples/sec: {count}")

if __name__ == "__main__":
    p = ArgumentParser(description="Magnetometer poller and MQTT publisher.")
    p.add_argument('-b', '--bus', type=int, default=1, help="I2C bus where the sensor is connected.")
    p.add_argument('-a', '--i2caddr', type=int, default=0xc, help="Sensor I2C address.")
    p.add_argument('-t', '--topic', default='mag', help="MQTT topic used to publish samples.")
    p.add_argument('-d', '--delay', type=float, default=0.01, help="Minimum delay between samples [ms].")
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
