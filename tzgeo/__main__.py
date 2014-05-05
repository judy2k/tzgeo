#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function

import argparse
import sys

import tzgeo


def main(argv=sys.argv[1:]):
    aparser = argparse.ArgumentParser()
    aparser.add_argument('lat')
    aparser.add_argument('lon')

    args = aparser.parse_args(argv)
    result = tzgeo.tzlookup(args.lat, args.lon)
    if result is not None:
        print(result)
        exit(0)
    else:
        print(
            "No timezone could be found for lat {lat} and lon {lon}.".format(
                lat=args.lat, lon=args.lon),
            file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()
