"""
Integrating some standard python types with the ArgumentParser.
"""

import datetime
import pathlib
import re
import ipaddress

from .spec import register_spec


################################################################################
# datetime.date and datetime.datetime

DATE_FORMAT = '%Y-%m-%d'
BASE_DATETIME_FORMAT = DATE_FORMAT + 'T%H:%M:%S'


def _parse_date(s):
    return datetime.datetime.strptime(s, DATE_FORMAT).date()


def _parse_datetime(s):
    PATTERNS = [
        '%s%s%s' % (base, milli, z)
        for base in [BASE_DATETIME_FORMAT]
        for milli in ['', '.%f']
        for z in ['', 'Z']
    ]
    for p in PATTERNS:
        try:
            return datetime.datetime.strptime(s, p)
        except ValueError:
            pass
    raise ValueError(s)


for x in [datetime.date, 'date']:
    register_spec(
        x,
        dict(
            names=['date', 'd'],
            from_string=_parse_date,
            metavar='DATE',
            help='a date (YYYY-MM-DD)'
        ),
    )


for x in [datetime.datetime, 'datetime']:
    register_spec(
        x,
        dict(
            names=['timestamp', 't'],
            from_string=_parse_datetime,
            metavar='TIMESTAMP',
            help='a timestamp (ISO 8601: YYYY-MM-DDTHH:MM:SS[.micros][Z])'
        ),
    )


################################################################################
# pathlib.Path

for x in [pathlib.Path, 'path']:
    register_spec(
        x,
        dict(
            names=['path'],
            from_string=pathlib.Path,
            metavar='PATH',
        ),
    )


################################################################################
# regex

register_spec(
    'regex',
    dict(
        names=['regex'],
        from_string=re.compile,
        metavar='REGEX',
        help='a regular expression',
    ),
)


################################################################################
# IP address / hostname

register_spec(
    'ipaddress',
    dict(
        names=['ip'],
        from_string=ipaddress.ip_address,
        metavar='IP',
        help='an IP address, e.g. "192.168.0.1" or "2001:db8::"'
    ),
)

################################################################################
