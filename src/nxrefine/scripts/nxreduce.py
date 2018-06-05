#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Copyright (c) 2018, NeXpy Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING, distributed with this software.
#-----------------------------------------------------------------------------
import argparse
from nxrefine.nxreduce import NXReduce


def main():

    parser = argparse.ArgumentParser(
        description="Perform data reduction on entries")
    parser.add_argument('-d', '--directory', required=True, 
                        help='scan directory')
    parser.add_argument('-e', '--entries', default=['f1', 'f2', 'f3'], 
        nargs='+', help='names of entries to be processed')
    parser.add_argument('-t', '--threshold', type=float,
                        help='peak threshold - defaults to maximum counts/10')
    parser.add_argument('-f', '--first', type=int, help='first frame')
    parser.add_argument('-l', '--last', type=int, help='last frame')
    parser.add_argument('-r', '--refine', action='store_true',
                        help='refine lattice parameters')
    parser.add_argument('-t', '--transform', action='store_true',
                        help='perform CCTW transforms')
    parser.add_argument('-o', '--overwrite', action='store_true', 
                        help='overwrite existing maximum')

    args = parser.parse_args()

    for entry in args.entries:
        reduce = NXReduce(entry, args.directory, threshold=args.threshold, 
                          first=args.first, last=args.last,
                          refine=args.refine, transform=args.transform, 
                          overwrite=args.overwrite)
        reduce.nxreduce()


if __name__=="__main__":
    main()