# tzgeo

tzgeo is a Python library with one simple purpose - to convert a lat/lon to a
timezone - really fast!

## Installation

The easiest way to install is using `pip`

```shell
pip install tzgeo
```

If you're lucky, this will install okay.

tzgeo relies on the [pyspatialite] library, and unfortunately that can be a
little difficult to install. If the installation of pyspatialite fails, try
running:

```shell
pip install pyspatialite --pre
pip install tzgeo
```

... and see if that works.

## Usage

Using tzgeo is very simple!

```python
>>> import tzgeo
>>> tzgeo.tz_lookup(39.888724, -75.107952)
u'America/New_York'
```

If the lat/lon is invalid, or points at the ocean, `tz_lookup` will return
`None`.

```python
>>> print(tzgeo.tz_lookup(0.0, 0.0))
None
```

## How Is This Done?

tzgeo includes a sqlite/spatialite database containing the the geographical
regions that make up each timezone. The data was obtained from
[whereonearth-timezone].

spatialite provides the ability to do fast lookup to see whether a polygon
contains a given point, so lookups in this database are pretty fast. The
underlying storage is also reasonable efficient, so the database is only
~35Mb.

## Are There Any Alternatives?

I wrote this to be a faster alternative to [tzwhere]. tzwhere is much easier to
install, because it has no external dependencies. If speed isn't your main
concern, that may be a better option.

## You Did Something Wrong!

If you have any problems installing or using the library, please create an
[issue](https://github.com/judy2k/tzgeo/issues/new)
describing the problem you're having, along with any information you think
might be useful.

I'm not a GIS expert, so I may have made a mistake. If you can suggest
improvements, please
[let me know](https://github.com/judy2k/tzgeo/issues/new). Even better,
submit a pull request with a fix!

## Todo

* Region limiting, for faster lookups, e.g. ```tz_lookup(lat, lon, 'America')```
  (This *might* make it faster, who knows?)
* Decide whether to calculate a timezone based on longitude if the location is
  in the sea.

[whereonearth-timezone]: https://github.com/straup/whereonearth-timezone
[pyspatialite]: https://github.com/lokkju/pyspatialite
[tzwhere]: https://github.com/mattbornski/tzwhere
