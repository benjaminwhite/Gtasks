import calendar
import datetime as dt
import time

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'
DATE_FORMAT = '%Y-%m-%dT00:00:00.000Z'
DPLUS_FORMAT = '%Y-%m-%dT00:01:00.000Z'

def valid_rfcformat(potential):
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
    elif valid_rfcformat(unknown):
        return unknown
    else:
        raise RFC3339ConversionError(unknown)

def from_rfc3339(rfc3339):
    time_tuple = time.strptime(rfc3339, DATETIME_FORMAT)
    utc_timestamp = calendar.timegm(time_tuple) 
    return dt.datetime.fromtimestamp(utc_timestamp)

def to_date_rfc3339(unknown, plus_a_min=False):
    if plus_a_min:
        rfc_format = DPLUS_FORMAT
    else:
        rfc_format = DATE_FORMAT
    if hasattr(unknown, 'strftime'):
        return unknown.strftime(rfc_format)
    elif type(unknown) in (float, int):
        return dt.date.fromtimestamp(unknown).strftime(rfc_format)
    elif valid_rfcformat(unknown):
        return to_date_rfc3339(from_date_rfc3339(unknown), plus_a_min)
    else:
        raise RFC3339ConversionError(unknown)

def from_date_rfc3339(rfc3339):
    return dt.datetime.strptime(rfc3339, DATE_FORMAT).date()

class RFC3339ConversionError(Exception):
    def __str__(self, culprit):
        return 'Could not convert {} to RFC 3339 timestamp.'.format(culprit)
