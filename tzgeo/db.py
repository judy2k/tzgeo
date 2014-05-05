# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import pyspatialite.dbapi2 as db


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
    SELECT tz_name
        FROM timezone
        WHERE Within(
            PointFromText(
                'POINT({lon} {lat})',
                4326
            ),
            geometry
        );
"""

INSERT_TIMEZONE_SQL = """
    INSERT INTO timezone (tz_name, geometry) VALUES (
      ?,
      MultiPolygonFromText(?, 4326)
    );
"""


def _bjoin(l):
    """
    Convert the sequence `l` into a string by joining with ', ' and then
    surrounding with parentheses.
    """
    return '(' + ', '.join(l) + ')'


def _fmt_linear_ring(linear_ring):
    return _bjoin('{0} {1}'.format(*point) for point in linear_ring)


def _fmt_poly(poly):
    return _bjoin([_fmt_linear_ring(linear_ring) for linear_ring in poly])


def multipolygon_to_wkt(mp):
    """
    Convert a GeoJSON-structured MultiPolygon or Polygon dict to a WKT
    MultiPolygon string.
    """
    if mp['type'] == 'MultiPolygon':
        polys = [_fmt_poly(poly) for poly in mp['coordinates']]
        return 'MULTIPOLYGON ' + _bjoin(polys)
    elif mp['type'] == 'Polygon':
        poly = _fmt_poly(mp['coordinates'])
        return 'MULTIPOLYGON (' + poly + ')'
    else:
        raise ValueError("Unsupported type: %s" % mp['type'])


class TimezoneLookupDB(object):
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self._connection = None

    def _connect(self):
        if self._connection is None:
            self._connection = db.connect(self.dbpath)

    def init_db(self):
        self._connect()
        self._connection.executescript(DDL)

    def timezone_for_point(self, lat, lon):
        self._connect()
        cur = self._connection.execute(
            POINT_WITHIN_SQL.format(lon=lon, lat=lat))
        row = next(cur, None)
        return row[0] if row else None

    def insert_timezone_geometry(self, tz_name, geometry):
        self._connect()
        self._connection.execute(
            INSERT_TIMEZONE_SQL,
            (tz_name, multipolygon_to_wkt(geometry))
        )

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()
