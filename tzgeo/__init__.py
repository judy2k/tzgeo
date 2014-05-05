import os.path

import pyspatialite.dbapi2 as db


DEFAULT_DBPATH = os.path.join(os.path.dirname(__file__), 'tzlookup.sqlite')

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
    select tz_name
        from timezone
        where Within(
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


def multipolygon_to_wkt(mp):
    """
    Convert a GeoJSON-structured multypolygon dict to a WKT string.
    """
    if mp['type'] == 'MultiPolygon':
        polys = []
        for poly in mp['coordinates']:
            poly_rings = []
            for linear_ring in poly:
                points = _bjoin('{0} {1}'.format(*point) for point in linear_ring)
                poly_rings.append(points)
            polys.append(_bjoin(poly_rings))
        return 'MULTIPOLYGON ' + _bjoin(polys)
    elif mp['type'] == 'Polygon':
        poly_rings = []
        for linear_ring in mp['coordinates']:
            points = _bjoin('{0} {1}'.format(*point) for point in linear_ring)
            poly_rings.append(points)
        return 'MULTIPOLYGON (' + _bjoin(poly_rings) + ')'


class TZGeo(object):
    def __init__(self, dbpath=DEFAULT_DBPATH):
        self.dbpath = dbpath
        self.connection = None

    def __call__(self, lat, lon):
        self._connect()
        cur = self.connection.execute(POINT_WITHIN_SQL.format(lon=lon, lat=lat))
        row = next(cur, None)
        return row[0] if row else None

    def _connect(self):
        if self.connection is None:
            # TODO: Check for any error handling here!
            self.connection = db.connect(self.dbpath)

        if self.dbpath == ':memory:':
            self._init_db()

    def _init_db(self):
        self._connect()
        self.connection.executescript(DDL)

    @staticmethod
    def _timezone_files():
        data_root = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                 'whereonearth-timezone/data')
        for root, dirs, files in os.walk(data_root):
            for f in files:
                if f.endswith('.geojson'):
                    path = os.path.join(root, f)
                    yield path

    def load_timezone_data(self):
        import geojson
        self._connect()

        try:
            self.connection.execute("DELETE FROM timezone")
            for path in self._timezone_files():
                with open(path) as fp:
                    data = geojson.load(
                        fp, object_hook=geojson.GeoJSON.to_instance)
                    feature = data['features'][0]
                    tz_name = feature['properties']['name']
                    self.connection.execute(
                        INSERT_TIMEZONE_SQL,
                        (tz_name, multipolygon_to_wkt(feature['geometry']))
                    )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def __del__(self):
        if self.connection is not None:
            self.connection.close()


tzlookup = TZGeo()

if __name__ == '__main__':
    tzlookup.load_timezone_data()
