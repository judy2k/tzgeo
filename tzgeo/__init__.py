# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

try:
    # simplejson is faster than json:
    import simplejson as json
except ImportError:
    import json

import os.path

from . import db


SOURCE_DATA_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'whereonearth-timezone/data')
DEFAULT_DBPATH = os.path.join(os.path.dirname(__file__), 'tzlookup.sqlite')


class TZGeo(object):
    """
    A callable object representing a connection to a tzlookup spatialite db.

    This class defers connecting to the sqlite database until a call is made
    that requires the connection because there is a default instance on the
    module, called `tzlookup`. We want the class to do as little work as
    possible on instantiation so that the module does as little work as
    possible on import.
    """

    def __init__(self, dbpath=DEFAULT_DBPATH):
        self._db = db.TimezoneLookupDB(dbpath)

    def __call__(self, lat, lon):
        """
        Lookup a timezone for the provided latitude and longitude.

        If no timezone region encompasses the provided point, this
        returns `None`.
        """
        return self._db.timezone_for_point(lat, lon)

    @staticmethod
    def _timezone_files(source_data_root):
        for root, dirs, files in os.walk(source_data_root):
            for f in files:
                if f.endswith('.geojson'):
                    path = os.path.join(root, f)
                    yield path

    def load_timezone_data(self, source_data_root=SOURCE_DATA_ROOT):
        """
        This is an internal method, used for updating the data contained in the
        spatialite db.
        """
        try:
            self._db.init_db()
            for path in self._timezone_files(source_data_root):
                with open(path) as fp:
                    data = json.load(fp)
                    feature = data['features'][0]
                    tz_name = feature['properties']['name']
                    self._db.insert_timezone_geometry(
                        tz_name, feature['geometry'])
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise


tzlookup = TZGeo()

if __name__ == '__main__':
    tzlookup.load_timezone_data()
