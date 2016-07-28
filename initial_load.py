# codingL utf-8
import dbapi
import ftplib
import datetime, os, sys, time
import functools

# --------------- Config -----------------
FTP_IP = '10.128.164.230'
FTP_USER = 'user'
FTP_PASSWORD = 'password'
FTP_DIR = ''

HANA_IP = '10.128.184.214'
HANA_PORT = '30015'
HANA_USER = 'I321761'
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
                        if i % batch_size == 0:
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


# --------------------------------- Check BUS card csv, if not exist download it via ftp

def log(f):
    now = lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @functools.wraps(f)
    def wrapper(*args):
        print '==> [{}] Start: {}()'.format(now(), f.__name__)
        result = f(*args)
        print '==> [{}] End  : {}(){}'.format(now(), f.__name__, os.linesep)
        return result

    return wrapper


@log
def prepare():
    csv_folder = os.path.abspath('./csv')
    if not os.path.exists(csv_folder):
        try:
            print 'Create directory:', csv_folder
            os.mkdir(csv_folder)
        except Exception as e:
            print 'Create folder failed:{}'.format(csv_folder)
            print e
            exit()


@log
def start():
    print 'argv:', sys.argv
    if len(sys.argv) < 2:
        usage()
        return False

    start_date, count = None, None
    try:
        start_date = str_to_date(sys.argv[1])
        if start_date:
            if len(sys.argv) > 2:
                end_date = str_to_date(sys.argv[2])
                delta_date = end_date - start_date
                count = delta_date.days + 1
            else:
                count = 1
    except Exception as e:
        start_date, count = None, None
        print e

    if not start_date or not count:
        usage()
        return False

    print 'Load time range: from {}, total {} days'.format(start_date, count)
    dates = [(start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(count)]
    print('All dates:{}'.format(dates))
    for date in dates:
        load(date)


@log
def import_bus_card_csv(csv):
    with Hana(HANA_IP, int(HANA_PORT), HANA_USER, HANA_PASSWORD) as hana:
        result = hana.insert(csv, "INSERT INTO T VALUES (?,?,?,?,?)", has_header=True)
        print result


@log
def download_csv(csv):
    csv_name = os.path.basename(csv)
    ftp = None
    result = False
    try:
        ftp = ftplib.FTP(FTP_IP)
        ftp.login(FTP_USER, FTP_PASSWORD)
        ftp.cwd(FTP_DIR)
        if csv_name in ftp.nlst():
            with open(csv, 'wb') as f:
                ftp.retrbinary('RETR %s' % csv, f.write)
                result = True
                print 'bus file ready'
        else:
            print 'no ' + csv_name + ' such file'
    except Exception as ex:
        print ex
    finally:
        if ftp:
            ftp.close()
    return result


@log
def load(date):
    print('... load date: {}'.format(date))
    csv = os.path.join(os.path.abspath('./csv/'), '%s.csv' % date)
    if not os.path.exists(csv):
        print '!!! Cannot find csv:%s' % csv
        if not download_csv(csv):
            return False

    import_bus_card_csv(csv)


def str_to_date(s):
    date = None
    try:
        date = datetime.datetime.strptime(s, "%Y-%m-%d")
    except Exception as e:
        print e
        print '{} is not a legal date'.format(s)
    return date


def usage():
    print 'Wrong parameter usage !!!'
    print '''Usage:
        Load single day:   python initialload.py 2016-07-06
        Load multiple day: python initialload.py 2016-07-06 2016-07-10
    '''


if __name__ == '__main__':
    prepare()
    start()
    
