"""
Integrating some standard python types with the ArgumentParser.

Included here:

- date (type=datetime.date or type='date')
- datetime (type=datetime.datetime or type='datetime')
- path (type=pathlib.Path or type='path')
- regular expressions (type='regex')
- IP address (type='ipaddress')

"""

import datetime
import pathlib
import logging
import ast
import re
import ipaddress

from .spec import register_spec


################################################################################
# range

def _parse_range(s):
    parts = [int(x) for x in s.split(':')]
    return range(*parts)


for _x in [range, 'range']:
    register_spec(
        _x,
        dict(
            from_string=_parse_range,
            metavar='RANGE',
            help='a range (START:STOP or START:STOP:STEP)'
        ),
    )


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


for _x in [datetime.date, 'date']:
    register_spec(
        _x,
        dict(
            names=['date', 'd'],
            from_string=_parse_date,
            metavar='DATE',
            help='a date (YYYY-MM-DD)'
        ),
    )


for _x in [datetime.datetime, 'datetime']:
    register_spec(
        _x,
        dict(
            names=['timestamp', 't'],
            from_string=_parse_datetime,
            metavar='TIMESTAMP',
            help='a timestamp (ISO 8601: YYYY-MM-DDTHH:MM:SS[.micros][Z])'
        ),
    )


################################################################################
# pathlib.Path

for _x in [pathlib.Path, 'path']:
    register_spec(
        _x,
        dict(
            names=['path'],
            from_string=pathlib.Path,
            metavar='PATH',
        ),
    )


################################################################################
# log level

def _parse_log_level(s):
    val = None
    try:
        # try int
        val = int(s)
    except ValueError:
        pass
    if val is None:
        for name in [s, s.upper()]:
            try:
                val = logging._nameToLevel[name]
                break
            except KeyError:
                pass
    if val is not None:
        try:
            return logging._levelToName[val]
        except KeyError:
            pass
    raise ValueError(s)


register_spec(
    'log_level',
    dict(
        names=['log-level', 'L'],
        from_string=_parse_log_level,
        metavar='LOG_LEVEL',
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
# literal

# NOTE: python-fire does the same thing, and much better.
# consider replacing this with its DefaultParseValue() function.
def _parse_literal(s):
    try:
        # ast.literal_eval supports the following types:
        # strings, bytes, numbers, tuples, lists, dicts, sets, booleans, and None
        return ast.literal_eval(s)
    except (SyntaxError, ValueError):
        # If literal_eval can't parse the value, treat it as a string.
        return s


register_spec(
    'literal',
    dict(
        from_string=_parse_literal,
        metavar='LITERAL',
        help='a python literal'
    ),
)


################################################################################
