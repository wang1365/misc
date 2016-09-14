# codingL utf-8
import dbapi
from kafka import KafkaProducer
import datetime, os, sys, time
import functools, datetime
import traceback

HANA_IP = '10.128.184.214'
HANA_PORT = '30015'
HANA_USER = 'ESPUSER'
HANA_PASSWORD = 'Sap12345'


# -----------------------------------------


class Hana(object):
    '''
    This class is used to query or set data to HANA database
    '''

    def __init__(self, ip, port, user, password):
        self.info = (ip, port, user, password)
        self.connection = None

        print('Start connect hana: {} {} {}'.format(*self.info[:3]))
        try:
            self.connection = dbapi.connect(*self.info)
        except Exception as e:
            print e

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.connection and self.connection.isconnected():
            self.connection.close()

    def get(self, sql):
        result = None
        try:
            if self.connection and self.connection.isconnected():
                print('Connect success')
                cursor = self.connection.cursor()
                print 'Execute sql:', sql
                cursor.execute(sql)
                print 'cursor param:', cursor.parameter_description()
                result = cursor.fetchall()
                #print 'result:', result
            else:
                print 'DB is not connected !!'
        except Exception as e:
            print e
            print traceback.format_exc()
        return result

    def insert(self, data_file, sql, has_header=True, batch_size=10000):
        result = None

        try:
            if self.connection and self.connection.isconnected():
                print('Connect success')
                cursor = self.connection.cursor()
                print 'Execute sql:', sql
                with open(data_file) as f:
                    batch = []
                    for i, line in enumerate(f):
                        batch.append(tuple(line.strip('\n').split(',')))
                        if i % batch_size == 0:
                            cursor.executemany(sql, batch)
                            batch = []
                    if batch:
                        cursor.executemany(sql, batch)

                #print 'result:', result
            else:
                print 'DB is not connected !!'
        except Exception as e:
            print e
        return result


def time2String(t):
    return t.strftime('%Y-%m-%d %X')


def now():
    return datetime.datetime.now() - datetime.timedelta(hours=8)


def add_minutes(dt, minute):
    return dt + datetime.timedelta(minutes=minute)

def format_msg(msg):
    if msg:
        # (u'\u82cfA73320', 31.203033, 121.763132, 0.0, datetime.datetime(2016, 9, 1, 9, 23, 33), 0, Decimal('0'),
        #  datetime.datetime(2016, 9, 1, 9, 23, 39))
        #return u'{}'.format(str(msg))
        #print msg

        #RECORD_ID, STATION_NO, LANE_NO,  PLATE_NUM, PLATE_COLOR, VEH_SPEED, COLLECT_TIME, CAP_TIME, RECEIVE_TIME

        return u'{},{},{},{},{},{},{},{},{}'.format(msg[0], msg[1], msg[2], msg[3], msg[4], msg[5], time2String(msg[6]), time2String(msg[7]), time2String(msg[8]))
    else:
        return ''

count = 0
def sendSingleMsg2Kafka(msg):
    if not msg:
        return
    producer = KafkaProducer(bootstrap_servers='10.128.184.167:9092')
    producer.send('topic_lpr', msg.encode('utf8'))
    producer.flush()
    producer.close(timeout=5)


def send2Kafka(msgs):
    if not msgs:
        return
    producer = KafkaProducer(bootstrap_servers='10.128.184.167:9092')

    global count
    for msg in msgs:
        tmp = format_msg(msg)
        # print 'Send ==> ', tmp
        producer.send('topic_lpr', tmp.encode('utf8'))
        if count % 100 == 0:
            print u'==>[{}] {}'.format(count, tmp)
            producer.flush()
        count += 1

    producer.flush()
    producer.close(timeout=5)


def start_trigger():
    from apscheduler.schedulers.background import BackgroundScheduler
    def trigger():
        print '[{}]========================= Trigger'.format(time2String(now()))
        snow = time2String(now() - datetime.timedelta(seconds=1))
        print 'Send trigger message:', snow
        sendSingleMsg2Kafka(snow)

    scheduler = BackgroundScheduler()
    scheduler.add_job(trigger, 'interval', seconds=60, start_date='2016-09-12 16:11:00')
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

def run():
    start_trigger()
    t1, t2 = None, now()
    sql = "SELECT RECORD_ID,STATION_NO,LANE_NO,TO_NVARCHAR(PLATE_NUM),PLATE_COLOR,VEH_SPEED, COLLECT_TIME, CAP_TIME, RECEIVE_TIME FROM ESPUSER.LPR WHERE RECEIVE_TIME >= '{}' AND RECEIVE_TIME < '{}'"
    while True:
        try:
            with Hana(HANA_IP, int(HANA_PORT), HANA_USER, HANA_PASSWORD) as hana:
                if t1:
                    t1, t2 = t2, now()
                else:
                    t1 = add_minutes(t2, -1)

                full_sql = sql.format(time2String(t1), time2String(t2))
                print full_sql
                result = hana.get(full_sql)
                #print result
                print 'Gen record count:', None if not result else len(result)
                send2Kafka(result)
        except Exception as e:
                print traceback.format_exc()
                print e
        time.sleep(10)


if __name__ == '__main__':
    run()
    pass
