import datetime

import strict_rfc3339 as sr3

def to_rfc3339(unknown):
    if hasattr(unknown, 'strftime'):
        unix_timestamp = float(unknown.strftime('%s'))
        return sr3.timestamp_to_rfc3339_utcoffset(unix_timestamp)
    elif type(unknown) in (float, int):
        return sr3.timestamp_to_rfc3339_utcoffset(unknown)
    elif sr3.validate_rfc3339(unknown):
        return unknown
    else:
        raise RFC3339ConversionError(unknown)

def rfc3339_compatible(unknown):
    return (hasattr(unknown, 'strftime') or type(unknown) in (float, int)
            or sr3.validate_rfc3339(unknown))

def from_rfc3339(rfc3339):
    return datetime.datetime.fromtimestamp(sr3.rfc3339_to_timestamp(rfc3339))

class RFC3339ConversionError(Exception):
    def __str__(self, culprit):
        return 'Could not extract a Unix timestamp from:\n{}'.format(culprit)
