# -*- coding: utf-8 -*-
"""
tzgeo
=====

tzgeo is a library with one simple purpose - to convert a lat/lon to a
timezone - really fast!


Installation
------------
The easiest way to install is using `pip`::

    pip install tzgeo


Usage
-----
Using tzgeo is very simple!

::

    >>> import tzgeo
    >>> tzgeo.tz_lookup(39.888724, -75.107952)
    u'America/New_York'


If the location is invalid, or points at the ocean, `tz_lookup` will return
`None`.


More Information
----------------
More information can be found on the project's `github page`_

.. _`github page`: https://github.com/judy2k/tzgeo
"""

from setuptools import setup

setup(
    name="tzgeo",
    version="0.0.4",
    description="Get the timezone for a location",
    long_description=__doc__,
    author='Mark Smith',
    author_email='mark.smith@practicalpoetry.co.uk',
    url='https://github.com/judy2k/tzgeo',
    license='MIT License',

    packages=['tzgeo'],
    include_package_data=True,
    package_data={'tzgeo': ['tzgeo.sqlite']},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'pyspatialite>=3.0.1-alpha-0',
    ],
    zip_safe=False,
)
