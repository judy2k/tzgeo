# -*- coding: utf-8 -*-

"""
Get the timezone for a location.

In most cases, all you need to do is import `tzgeo` and call the
`tz_lookup` function::

    >>> import tzgeo
    >>> tzgeo.tz_lookup(39.888724, -75.107952)
    u'America/New_York'

`tz_lookup` will return `None` if the location is not on land:

    >>> import tzgeo
    >>> print(tzgeo.tz_lookup(0.0, 0.0))
    None

`tzgeo` can also be used from the command-line::

    $ python -m tzgeo 39.888724 -75.107952
    America/New York

The command-line exits with 0 if a timezone region was found, and 1 if no
timezone region was available.
"""

from __future__ import absolute_import, print_function

from itertools import ifilter
import os.path

from . import db


__all__ = ['tz_lookup']
__version__ = '0.0.4'


SOURCE_DATA_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'whereonearth-timezone/data')

DEFAULT_DBPATH = os.path.join(os.path.dirname(__file__), 'tzgeo.sqlite')


tz_db = db.TimezoneLookupDB(DEFAULT_DBPATH)
tz_lookup = tz_db.tz_lookup


def _timezone_files(source_data_root):
    """
    Abstract generator to obtain paths to all the .geojson files in root.
    """
    for root, dirs, files in os.walk(source_data_root):
        for filename in ifilter(lambda f: f.endswith('.geojson'), files):
            path = os.path.join(root, filename)
            yield path


if __name__ == '__main__':
    # If this file is executed directly, it will create a new
    # tz_lookup database:
    tz_db.load_timezone_data(_timezone_files(SOURCE_DATA_ROOT))
