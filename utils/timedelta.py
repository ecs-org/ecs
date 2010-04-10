import re
from datetime import timedelta

def timedelta_to_seconds(td):
    return td.seconds + td.days * 3600 * 24 + td.microseconds * 0.000001

_timedelta_format_re = re.compile(r''''(?P<h1>\d{1,2})h
    |(?P<m1>\d{1,2})m(?:in)?
    |(?P<s1>\d{1,2})s(?:ec)?
    |(?:
        (?P<h2>\d{1,2})
        (?::
            (?P<m2>\d{1,2})
            (?::
                (?P<s2>\d{1,2})
            )?
        )?
    )
''', re.VERBOSE)

def parse_timedelta(s):
    bits = s.split(' ')
    secs = 0
    for bit in bits:
        bit = bit.strip()
        if not bit:
            continue
        match = _timedelta_format_re.match(bit)
        if match:
            m = match.group('m1') or match.group('m2')
            h = match.group('h1') or match.group('h2')
            s = match.group('s1') or match.group('s2')
            if m:
                secs += int(m) * 60
            if h:
                secs += int(h) * 3600
            if s:
                secs += int(s)
    return timedelta(seconds=secs)
            
            