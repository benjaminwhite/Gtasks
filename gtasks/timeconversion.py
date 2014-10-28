import calendar
import datetime as dt
import time

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'
DATE_FORMAT = '%Y-%m-%dT00:00:00.000Z'

def valid_rfc3339(potential):
    try:
        dt.datetime.strptime(potential, DATETIME_FORMAT)
        return True
    except:
        return False

def to_rfc3339(unknown):
    if hasattr(unknown, 'timetuple'):
        if hasattr(unknown, 'tzinfo') and unknown.tzinfo is not None:
            utc_timestamp = calendar.timegm(unknown.utctimetuple())
        else:
            utc_timestamp = time.mktime(unknown.timetuple())
        utc_datetime = dt.datetime.utcfromtimestamp(utc_timestamp)
        return utc_datetime.strftime(DATETIME_FORMAT)
    elif type(unknown) in (float, int):
        utc_datetime = dt.datetime.utcfromtimestamp(unknown)
        return utc_datetime.strftime(DATETIME_FORMAT)
    elif valid_rfc3339(unknown):
        return unknown
    else:
        raise RFC3339ConversionError(unknown)

def from_rfc3339(rfc3339):
    time_tuple = time.strptime(rfc3339, DATETIME_FORMAT)
    utc_timestamp = calendar.timegm(time_tuple) 
    return dt.datetime.fromtimestamp(utc_timestamp)

def valid_date_rfc3339(potential):
    try:
        dt.datetime.strptime(potential, DATE_FORMAT)
        return True
    except:
        return False

def to_date_rfc3339(unknown):
    if hasattr(unknown, 'strftime'):
        return unknown.strftime(DATE_FORMAT)
    elif type(unknown) in (float, int):
        return dt.date.fromtimestamp(unknown).strftime(DATE_FORMAT)
    elif valid_date_rfc3339(unknown):
        return unknown
    else:
        raise RFC3339ConversionError(unknown)

def from_date_rfc3339(rfc3339):
    return dt.datetime.strptime(rfc3339, DATE_FORMAT).date()

class RFC3339ConversionError(Exception):
    def __str__(self, culprit):
        return 'Could not convert {} to a RFC 3339 timestamp.'.format(culprit)

if __name__ == '__main__':
    now = dt.datetime.now()
    today = dt.date.today()
    timestamp = time.time()
    print('Datetime: {}'.format(to_rfc3339(now)))
    print('Date: {}'.format(to_rfc3339(today)))
    print('Timestamp: {}'.format(to_rfc3339(timestamp)))

    tricky = dt.datetime(2014, 10, 27, 23, 59, 59)
    print('Tricky:'.format(to_rfc3339(tricky)))

    rfc_3339 = '2014-10-28T00:00:00.000Z'
    rfc_date = from_rfc3339(rfc_3339)
    print('{} converted to {}'.format(rfc_3339, rfc_date))
    print(rfc_date > now)

    print(now)
    print(to_rfc3339(now))
    print(from_rfc3339(to_rfc3339(now)))

    print('ARROW:')
    import arrow
    anow = arrow.now()
    achig = anow.to('-03:00')

    print('Current time in two different timezones:')
    print(anow)
    print(achig)

    print('Those times in RFC 3339:')
    print(to_rfc3339(anow))
    print(to_rfc3339(achig))

    print('Those times in datetime (after being rfc\'d):')
    print(from_rfc3339(to_rfc3339(anow)))
    print(from_rfc3339(to_rfc3339(achig)))


