# -*- coding: utf-8 -*-

"""
Internal module used to abstract the tzgeo spatialite database.

This module would not normally be used directly unless using a different
data-store, or loading data into the database from a different source.
"""

from __future__ import absolute_import, print_function

try:
    # simplejson is faster than json:
    import simplejson as json
except ImportError:
    import json

import pyspatialite.dbapi2 as spatialite


DDL = """
    SELECT InitSpatialMetaData();
    CREATE TABLE timezone (
        lc_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        tz_name TEXT NOT NULL);
    SELECT AddGeometryColumn(
      'timezone', 'geometry', 4326, 'MULTIPOLYGON', 'XY', 1);
    SELECT CreateSpatialIndex('timezone', 'geometry');
"""

POINT_WITHIN_SQL = """
SELECT tz.tz_name
    FROM timezone AS tz
    WHERE tz.ROWID IN
    (
        SELECT ROWID
        FROM idx_timezone_geometry
        WHERE xmin < ? AND xmax > ? AND ymin < ? AND ymax > ?
    )
    AND Contains(geometry, MAKEPOINT( ?, ?))
"""


INSERT_TIMEZONE_SQL = """
    INSERT INTO timezone (
        tz_name,
        geometry
    ) VALUES (
        ?,
        MultiPolygonFromText(?, 4326)
    );
"""


def _bjoin(seq):
    """
    Convert the sequence `seq` into a string by joining with ', ' and
    surrounding with parentheses.
    """
    return '(' + ', '.join(seq) + ')'


def _fmt_linear_ring(linear_ring):
    return _bjoin('{0} {1}'.format(*point) for point in linear_ring)


def _fmt_poly(poly):
    return _bjoin([_fmt_linear_ring(linear_ring) for linear_ring in poly])


def multipolygon_to_wkt(geometry):
    """
    Convert a GeoJSON MultiPolygon or Polygon dict to a WKT
    MultiPolygon string.
    """
    if geometry['type'] == 'MultiPolygon':
        polys = [_fmt_poly(poly) for poly in geometry['coordinates']]
        return 'MULTIPOLYGON ' + _bjoin(polys)
    elif geometry['type'] == 'Polygon':
        poly = _fmt_poly(geometry['coordinates'])
        return 'MULTIPOLYGON (' + poly + ')'
    else:
        raise ValueError("Unsupported type: %s" % geometry['type'])


def wkt_point(lat, lon):
    """
    Convert the provided lat, lon into a WKT Point string.
    """
    return 'POINT({lon} {lat})'.format(lat=lat, lon=lon)


class TimezoneLookupDB(object):
    """
    A timezone lookup database, backed by spatialite.

    This class only connects to the sqlite database when a call is made that
    requires the connection.
    """

    def __init__(self, db_path):
        self.db_path = db_path
        self._connection = None

    def tz_lookup(self, lat, lon):
        """
        Obtain a timezone string matching the timezone at (`lat`, `lon`).

        If no timezone region is available for the location, it returns `None`.
        """
        lat = float(lat)
        lon = float(lon)
        self._connect()
        cur = self._connection.execute(POINT_WITHIN_SQL, (lon, lon, lat, lat, lon, lat))
        row = next(cur, None)
        return row[0] if row else None

    def load_timezone_data(self, source_data_files):
        """
        Create a new spatialite database from whereonearth-timezone data files.

        :param: source_data_files A list of paths to geojson files.
        """
        self._connect()
        try:
            self._connection.executescript(DDL)
            for path in source_data_files:
                data = json.load(open(path))
                feature = data['features'][0]
                tz_name = feature['properties']['name']
                self._insert_timezone_geometry(
                    self._connection, tz_name, feature['geometry'])
            self._connection.commit()
        except Exception:
            self._connection.rollback()
            raise

    def _connect(self):
        """ Connect to the database, if not already connected.
        """
        if self._connection is None:
            self._connection = spatialite.connect(self.db_path)

    @staticmethod
    def _insert_timezone_geometry(connection, tz_name, geometry):
        """
        Insert a new record into the database.

        :param: connection An open spatialite database connection
        :param: tzname The name of the timezone
        :param: geometry The geometry provided a as a GeoJSON Polygon or
            MultiPolygon dictionary.
        """
        connection.execute(
            INSERT_TIMEZONE_SQL,
            (tz_name, multipolygon_to_wkt(geometry))
        )


