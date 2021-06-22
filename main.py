import serial
import time
import json

from datetime import datetime as dt
from pytz import timezone

from pathlib import Path
import sqlite3

def execute(
    port: str,
    baudrate: int,
    tz: str,
    db_path: Path,
):
    ser = serial.Serial(port, baudrate)
    time.sleep(3) # Wait connection established

    while True:
        r = ser.readline()

        try:
            pkt = json.loads(r.decode('ascii'))

            if 'light' in pkt and 'humidity' in pkt and 'temperature' in pkt:
                break
        except:
            print('Retry, %s' % r)
            pass

    ser.close()


    now_aware = dt.now(timezone(tz))

    light = pkt['light']
    humidity = pkt['humidity']
    temperature = pkt['temperature']
    timestamp = now_aware.isoformat()

    print(timestamp, pkt)

    db.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS sensor(id INTEGER PRIMARY KEY AUTOINCREMENT, light INTEGER, humidity INTEGER, temperature INTEGER, timestamp DATETIME)')

    cur.execute('INSERT INTO sensor VALUES(?,?,?,?,?)', (None, light, humidity, temperature, timestamp, ))

    db.commit()
    db.close()


if __name__ == '__main__':
    import configargparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', env_var='PORT', type=str, default='/dev/ttyUSB0')
    parser.add_argument('-b', '--baudrate', env_var='BAUDRATE',type=int, default=38400)
    parser.add_argument('-t', '--timezone', env_var='TIMEZONE',type=str, default='Asia/Tokyo')
    parser.add_argument('-o', '--db_path', env_var='DB_PATH',type=str, default='data/sensordb.sqlite3')
    args = parser.parse_args()

    def call():
        execute(
            port=args.port,
            baudrate=args.baudrate,
            tz=args.timezone,
            db_path=args.db_path,
        )

    import schedule
    schedule.every(5).seconds.do(call)

    while True:
        schedule.run_pending()
        time.sleep(1)
