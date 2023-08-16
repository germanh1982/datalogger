#!/usr/bin/python3
from matplotlib import pyplot
from matplotlib.animation import FuncAnimation
import paho.mqtt.client as mqttclient
import queue
from argparse import ArgumentParser
from json import loads
import numpy as np

if __name__ == '__main__':
    p = ArgumentParser()
    p.add_argument('--hist', '-i', type=int, default=6000, help="History points")
    p.add_argument('--dump', '-d', action='store_true')
    p.add_argument('host', help="MQTT server address")
    p.add_argument('topic', help="MQTT topic to subscribe for samples")
    p.add_argument('field', help="Graph this field value from the JSON payload")
    p.add_argument('labels')
    args = p.parse_args()

    labels = args.labels.split(',')
    linecount = len(labels)

    in_data = np.full((args.hist, 1 + linecount), np.NaN)

    c = mqttclient.Client()
    c.connect(args.host)

    q = queue.Queue()

    def on_message(client, userdata, message):
        js = loads(message.payload)
        q.put_nowait((js['ts'], *js[args.field]))

    c.on_message = on_message
    c.subscribe(args.topic)
    c.loop_start()

    figure = pyplot.figure()
    lines = [pyplot.plot(in_data[:,0], in_data[:,1 + i], label=labels[i])[0] for i in range(linecount)]
    pyplot.grid()
    pyplot.legend()

    def update(frame):
        global in_data, dcb, dcb_zi

        while True:
            try:
                newdata = q.get_nowait()
            except queue.Empty:
                break
            else:
                # rotate and append last sample to samples array 
                if args.dump:
                    print(','.join((str(x) for x in newdata)))
                in_data = np.roll(in_data, -1, axis=0)
                in_data[-1] = newdata

        # set line data
        for i in range(linecount):
            lines[i].set_data(in_data[:,0], in_data[:,1 + i])

        # autoscale graph with new samples
        figure.gca().relim()
        figure.gca().autoscale_view()

        return lines

    animation = FuncAnimation(figure, update, interval=20, cache_frame_data=True)
    pyplot.show()
