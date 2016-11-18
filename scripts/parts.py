#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright 2016 the HERA Collaboration
# Licensed under the 2-clause BSD license.

"""This is meant to hold utility scripts for handling parts and connections

"""
from __future__ import absolute_import, division, print_function

from hera_mc import part_connect, mc, part_handling

if __name__ == '__main__':
    handling = part_handling.PartsAndConnections()
    parser = mc.get_mc_argument_parser()
    parser.add_argument('-p', '--hpn', help="Get part information. [None]", default=None)
    parser.add_argument('-t', '--hptype', help="List the hera part types. [False]", action='store_true')
    parser.add_argument('-v', '--verbosity', help="Set verbosity {l, m, h}. [h].", default="h")
    parser.add_argument('-c', '--connection', help="Show all connections directly to a part. [None]", default=None)
    parser.add_argument('-u', '--update', help="Update part number records.  Format hpn0:col0:val0, [hpn1:]col1:val1...  [None]", default=None)
    parser.add_argument('-m', '--mapr', help="Show full hookup chains from given part. [None]", default=None)
    parser.add_argument('--specify_port', help="Define desired port(s) for hookup. [all]", default='all')
    parser.add_argument('--show_levels', help="Show power levels if enabled (and able) NOT YET IMPLEMENTED", action='store_true')
    parser.add_argument('--exact_match', help="Force exact matches on part numbers, not beginning N char. [False]", action='store_true')
    parser.add_argument('--add_new_part', help="Flag to allow update to add a new record.  [False]", action='store_true')
    parser.add_argument('--mapr_cols', help="Specify a subset of parts to show in mapr, comma-delimited no-space list. [all]",default='all')
    parser.add_argument('--levels_testing', help="Set to testing filename if correlator levels not accessible [False]", default=False)
    args = parser.parse_args()
    args.verbosity = args.verbosity.lower()
    args.mapr_cols = args.mapr_cols.lower()
    if args.hpn:
        args.hpn = args.hpn.upper()
        part_dict = handling.get_part(args, show_part=True)
    if args.connection:
        args.connection = args.connection.upper()
        connection_dict = handling.get_connection(args, show_connection=True)
    if args.mapr:
        args.mapr = args.mapr.upper()
        hookup_dict = handling.get_hookup(args, show_hookup=True)
    if args.hptype:
        part_type_dict = handling.get_part_types(args, show_hptype=True)
    if args.update:
        data = part_connect.parse_update_request(args.update)
        part_connect.update(args, data)
