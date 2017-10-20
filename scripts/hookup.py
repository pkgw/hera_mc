#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright 2017 the HERA Collaboration
# Licensed under the 2-clause BSD license.

"""This is meant to hold utility scripts for hookup

"""
from __future__ import absolute_import, division, print_function

from hera_mc import cm_hookup, cm_utils, mc
import os.path

if __name__ == '__main__':
    parser = mc.get_mc_argument_parser()
    parser.add_argument('-p', '--hpn', help="Part number, csv-list (required). [None]", default=None)
    parser.add_argument('-r', '--revision', help="Specify revision or last/active/full/all for hpn.  [LAST]", default='LAST')
    parser.add_argument('-e', '--exact-match', help="Force exact matches on part numbers, not beginning N char. [False]",
                        dest='exact_match', action='store_true')
    parser.add_argument('-q', '--quick', help="Shortcut to show a subset of cols and correlator level", action='store_true')
    parser.add_argument('--port', help="Define desired port(s) for hookup. [all]", dest='port', default='all')
    parser.add_argument('--show-state', help="Show 'full' or 'all' hookups [full]", dest='show_state', default='full')
    parser.add_argument('--hookup-cols', help="Specify a subset of parts to show in mapr, comma-delimited no-space list. [all]",
                        dest='hookup_cols', default='all')
    parser.add_argument('--show-levels', help="Show power levels if enabled (and able) [False]", dest='show_levels', action='store_true')
    parser.add_argument('--show-ports', help="Show ports on hookup.", dest='show_ports', action='store_true')
    parser.add_argument('--show-revs', help="Show revs on hookup.", dest='show_revs', action='store_true')
    cm_utils.add_date_time_args(parser)

    args = parser.parse_args()

    date_query = cm_utils._get_astropytime(args.date, args.time)

    # Pre-process the args
    args.hpn = cm_utils.listify(args.hpn)
    args.hookup_cols = cm_utils.listify(args.hookup_cols)
    if args.quick:
        args.show_levels = True
        args.hookup_cols = ['station', 'front-end', 'cable-post-amp(in)', 'post-amp', 'cable-container', 'f-engine', 'level']

    # Start session
    db = mc.connect_to_mc_db(args)
    session = db.sessionmaker()
    hookup = cm_hookup.Hookup(session)
    hookup_dict = hookup.get_hookup(hpn_list=args.hpn, rev=args.revision, port_query=args.port,
                                    at_date=date_query, exact_match=args.exact_match,
                                    show_levels=args.show_levels)
    hookup.show_hookup(hookup_dict=hookup_dict, cols_to_show=args.hookup_cols, show_levels=args.show_levels,
                       show_ports=args.show_ports, show_revs=args.show_revs, show_state=args.show_state)
