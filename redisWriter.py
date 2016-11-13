# -*- coding: utf8 -*-

import redis, datetime, types
import codecs

TAXI_CSV = '/opt/RAW_DATA/TAXI_BACKUP/BK_2015-11-24/20151124.csv'
SRC_UTC_FLAG = False
TAR_UTC_FLAG = True
DATETIME_FORMATTER = '%Y-%m-%d %X'


# Sample taxi GPS point
# VEHICLE_TYPE, VEHICLE_MODEL, VEHICLE_NUM,  PLATE_COLOR, RECORD_TIME ,        LONGITUDE,LATITUDE, STOWAGE, ALARM, OVER_SPEED_TIME, SPEED, DIRECTION, ALTITUDE, BUS_ROUTE, BUS_DIRECTION, RECEIVE_TIME
# 20,       A1,                苏A88322,     2,           2015-11-23 23:27:00, 118.69173,32.18058, 0,       0,     28800,           0.0,    0.0,      0.0,       ,         ,              2015-11-23 23:27:26, 2015-11-23 23:27:00,23:25:00,50616,320100,'
# 0         1                  2             3            4                    5         6         7        8      9                10      11        12         13        14             15
taxi_point = '20,A1,苏A88322,2,2015-11-23 23:27:00,118.69173,32.18058,0,0,28800,0.0,0.0,0.0,,,2015-11-23 23:27:26,2015-11-23 23:27:00,23:25:00,50616,320100,'


def localtoutc(t):
    st = datetime.datetime.strptime(t, DATETIME_FORMATTER) + datetime.timedelta(hours=-8)
    return st.strftime(DATETIME_FORMATTER)


class TaxiCSVParser(object):
    def __init__(self, name):
        self.name = name

    @staticmethod
    def __format(src):
        key, value = None, None
        try:
            # "DEVID", "LAT", "LNG", "SPEED", "GPS_TIME", "HEADING", "PASSENGER_STATE", "RECEIVE_TIME"
            s = src.split(',')
            gps_time, receive_time = localtoutc(s[4]), localtoutc(s[15])
            key = 'taxi_%s' % receive_time
            value = u'%s,%s,%s,%s,%s,%s,%s,%s' % (s[2], s[6], s[5], s[10], gps_time, s[11], s[7], receive_time)
        except Exception as e:
            print 'format failed:', src, e
        return key, value

    def gen(self):
        with codecs.open(TAXI_CSV, mode='r', encoding='utf8') as f:
            for line in f:
                yield self.__format(line)


class RedisIO(object):
    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(host=host, port=port)
        self.pipeline = self.redis.pipeline()

    def add_to_list(self, list_name, value):
        if not isinstance(list_name, (str, unicode)) or not isinstance(value, (str, unicode)):
            print 'Invalid type', list_name, value
        else:
            self.pipeline.rpush(list_name, value)

    def commit(self):
        self.pipeline.execute()

    def get_list(self, name):
        if not isinstance(name, str, unicode):
            print 'Invalid type', name
            return None
        count = self.redis.llen(name)
        return self.redis.lrange(0, count - 1)

    def clear_server_data(self):
        print '!!! Start to clear all server data'
        self.redis.flushall()
        print '!!! Clear done'

    def save(self):
        self.redis.save()

if __name__ == '__main__':
    parser = TaxiCSVParser(TAXI_CSV)
    redis = RedisIO(host='10.128.184.167')
    redis.clear_server_data()

    count = 0
    for k, v in parser.gen():
        redis.add_to_list(k, v)
        count = count + 1
        if count % 2000 == 0:
            print 'insert to redis:', count, k, v
            redis.commit()
            # redis.save()
    redis.commit()
    print 'insert to redis:', count
