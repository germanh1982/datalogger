#!/usr/bin/python3
import sqlite3
import sys
import logging
from argparse import ArgumentParser
import os
import datetime

def main():
    logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger()

    p = ArgumentParser()
    p.add_argument('--file', '-f', help='File name where to save samples.')
    args = p.parse_args()

    fname = args.file
    if fname is None:
        fname = 'samples-{}.db'.format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
        print(f"Saving to file {fname}")

    if os.path.exists(fname):
        raise RuntimeError(f"Output file {fname} already exists.")

    db = sqlite3.connect(fname)
    db.execute("CREATE TABLE IF NOT EXISTS samples (t REAL NOT NULL, x REAL NOT NULL, y REAL NOT NULL, z REAL NOT NULL)")

    try:
        for line in sys.stdin:
            values = line.strip('\n').split(',')
            db.execute("insert into samples (t, x, y, z) values (?, ?, ?, ?)", values)

    except Exception as e:
        log.exception(f"Exception raised: {str(e)}")

    finally:
        db.commit()

if __name__ == "__main__":
    main()
