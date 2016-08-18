"""Simple tool to mark times when the weather was misbehaving.

We mark misbehaving weather via a text file, with rows:

563628, 563667
or
2016-08-10T07:21, 2016-08-10T09:41

The first format marks exposure IDs, inclusive, that were taken in bad
conditions, and the second format marks times in UT.
"""

import numpy
from astropy.io import ascii
from astropy.time import Time


def check_bad(dat, badfile):
    conditions = get_conditions(dat, badfile)
    return conditions == 'bad'


def get_conditions(dat, badfile):
    badlist = ascii.read(badfile, delimiter=',')
    conditions = numpy.zeros(len(dat), dtype='a200')
    for row in badlist:
        field = None
        try:
            start = int(row['start'])
            end = int(row['end'])
            field = 'expnum'
        except ValueError:
            pass
        try:
            start = Time(row['start'], format='isot', scale='utc')
            end = Time(row['end'], format='isot', scale='utc')
            start = start.mjd
            end = end.mjd
            field = 'mjd_obs'
        except ValueError:
            pass
        if field is None:
            raise ValueError('row format not understood: %s' % row)
        if start > end:
            print(row)
            raise ValueError('file not understood, start > end')
        condition = row['type'].strip()
        if condition != 'bad':
            continue
        for f in 'grizy':
            val = dat[f+'_'+field]
            m = (val >= start) & (val <= end)
            conditions[m] = val[m]
    return conditions
