#!/usr/bin/python3
import sqlite3
from argparse import ArgumentParser
import os
import datetime
import paho.mqtt.client as mqttc
import json
from queue import Queue
from time import time

subscribe_topics = ['imu', 'mag', 'pres']

def main():
    fname = args.file
    if fname is None:
        fname = 'samples-{}.db'.format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        print(f"Saving to file {fname}")

    if os.path.exists(fname):
        raise RuntimeError(f"Output file {fname} already exists.")

    db = sqlite3.connect(fname)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS acc (t REAL NOT NULL, x REAL NOT NULL, y REAL NOT NULL, z REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS gyr (t REAL NOT NULL, x REAL NOT NULL, y REAL NOT NULL, z REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS mag (t REAL NOT NULL, x REAL NOT NULL, y REAL NOT NULL, z REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS pres (t REAL NOT NULL, temp REAL NOT NULL, pres REAL NOT NULL);
        """
    )

    q = Queue()

    client = mqttc.Client()
    client.connect(args.server)

    def onmsg(client, userdata, message):
        dic = json.loads(message.payload)
        q.put_nowait((message.topic, dic))

    client.on_message = onmsg
    for topic in subscribe_topics:
        client.subscribe(topic)
    client.loop_start()

    lastcommit = time()
    try:
        while True:
            topic, payload = q.get()

            if topic == 'imu':
                db.execute("insert into acc (t, x, y, z) values (?, ?, ?, ?)", (payload['ts'], *payload['acc']))
                db.execute("insert into gyr (t, x, y, z) values (?, ?, ?, ?)", (payload['ts'], *payload['gyr']))
            elif topic == 'mag':
                db.execute("insert into mag (t, x, y, z) values (?, ?, ?, ?)", (payload['ts'], *payload['mag']))
            elif topic == 'pres':
                db.execute("insert into pres (t, temp, pres) values (?, ?, ?)", (payload['ts'], payload['temp'], payload['pres']))

            # commit to disk every 5 seconds
            if time() - lastcommit > 5:
                db.commit()
                lastcommit = time()

    except KeyboardInterrupt:
        pass

    finally:
        print("Committing to disk..")
        db.commit()

if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument('-s', '--server', default='localhost')
    p.add_argument('--file', '-f', help='File name where to save samples.')
    args = p.parse_args()

    main()
