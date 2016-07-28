# coding: utf-8

import dbapi
import requests
import os, sys, json, math, time
import itertools
import multiprocessing


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
                result = cursor.fetchall()
                print 'result:', result
            else:
                print 'DB is not connected !!'
        except Exception as e:
            print e
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
                        if i%batch_size == 0:
                            cursor.executemany(sql, batch)
                            batch = []
                    if batch:
                        cursor.executemany(sql, batch)

                print 'result:', result
            else:
                print 'DB is not connected !!'
        except Exception as e:
            print e
        return result


def get_route(lat1, lng1, lat2, lng2):
    url = 'https://valhalla.mapzen.com/route'
    params = {
        'api_key': 'valhalla-7UikjOk',
        'json': {
            "locations": [{"lat": 32.06155521785999, "lon": 118.6618709564209},
                        {"lat": 32.059591226352595, "lon": 118.66474628448485}],
            "costing": "bicycle",
            "directions_options": {"units": "km", "language": "en-US"}
        }
    }
    headers = {
        'Host': 'valhalla.mapzen.com',
        'Origin': 'https://www.openstreetmap.org',
        'Referer': 'https://www.openstreetmap.org/directions?engine=mapzen_bicycle&route=32.0616%2C118.6619%3B32.0596%2C118.6647',
        'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36'
    }

    def make_params(lat1, lng1, lat2, lng2):
        params['json']['locations'] = [{"lat": str(lat1), "lon": str(lng1)}, {"lat": str(lat2), "lon": str(lng2)}]
        params['json'] = json.dumps(params['json'])
        return params

    body = make_params(lat1, lng1, lat2, lng2)
    r = requests.get(url, params=body, headers=headers, proxies={ 'http':'proxy.pal.sap.corp:8080', 'https':'proxy.pal.sap.corp:8080'})
    if not r.ok or not r.content:
        print 'Get failed', r.reason
        return None

    data = json.loads(r.content)
    try:
        route = data['trip']['legs'][0]['shape']
    except Exception as e:
        print e
        return False

    return route


def worker(name, station_pairs):
    def get_stations_coordinates(s):
        return (s[0][1], s[0][2], s[1][1], s[1][2])

    process_name = multiprocessing.current_process().name
    total = len(station_pairs)
    with open(name, 'w') as f:
        for i, s in enumerate(station_pairs):
            route = get_route(*get_stations_coordinates(s))
            print '{}: process {}/{}'.format(process_name, i + 1, total)
            sys.stdout.flush()

            record = '{from_station_id},{to_station_id},{route},{route_linestr}\n'.format(from_station_id=s[0][0],
                                                                                        to_station_id=s[1][0],
                                                                                        route=route, route_linestr='')
            f.write(record)
            f.flush()
            time.sleep(0.2)


def start(process_count=10):
    data = None
    with Hana('10.128.184.214', 30015, 'I321761', 'Sap12345') as hana:
        sql = '''
        select  "STATION_ID", "LAT", "LNG", "CAPACITY"
        from "SAP_ITRAFFIC_DEMO"."sap.traffic.demo.ptm.s.db::BIKE.GIS.STATION"
        '''
        data = hana.get(sql)

    if not data:
        print 'Cannot get data from Hana'
        return False

    print 'Get bike stations count:', len(data)

    station_pairs = [i for i in itertools.combinations(data, 2)]

    total = len(station_pairs)
    count = int(math.ceil(float(total)/process_count))

    print '===> Total {} station pairs, use {} processes to fetch data, each process handles {}'.format(total, process_count, count)
    #for i in range(process_count):
    for i in range(process_count):
        start_idx, end_idx = count*i, total if count*(i+1) > total else count*(i+1)
        p = multiprocessing.Process(name="Process%d"%(i+1), target=worker, args=('data%d.csv'%i, station_pairs[start_idx:end_idx]))
        p.start()
        #p.join()


if __name__ == '__main__':
    #get_route(32.06155521785999, 118.6618709564209, 32.059591226352595, 118.66474628448485)
    start()
