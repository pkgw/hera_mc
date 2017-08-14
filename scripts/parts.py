#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright 2016 the HERA Collaboration
# Licensed under the 2-clause BSD license.

"""This is meant to hold utility scripts for handling parts and connections

"""
from __future__ import absolute_import, division, print_function

from hera_mc import part_connect, cm_handling, cm_utils, mc
import os.path

if __name__ == '__main__':
    parser = mc.get_mc_argument_parser()
    # Actions are:  mapr, type, part_info, conn_info, rev_info, check_rev, overlap_check, update
    parser.add_argument('action', nargs='?', help="Actions are:  mapr, type, part_info, conn_info, rev_info, \
                                                   check_rev, overlap_check, update", default='mapr')

    # set values for 'action' to use
    parser.add_argument('-p','--hpn', help="Part number (required). [None]", default=None)
    parser.add_argument('-r','--revision', help="Specify revision or last/active/full/all for hpn.  [LAST]", default='LAST')
    parser.add_argument('-e','--exact-match', help="Force exact matches on part numbers, not beginning N char. [False]", 
                                              dest='exact_match', action='store_true')
    parser.add_argument('--specify-port', help="Define desired port(s) for hookup. [all]", dest='specify_port', default='all')
    parser.add_argument('--show_state', help="Show only the 'active' parts or all [all]", default='all')
    parser.add_argument('--mapr-cols', help="Specify a subset of parts to show in mapr, comma-delimited no-space list. [all]",
                                       dest='mapr_cols', default='all')
    parser.add_argument('--full-req', help="hookup columns needed to constitute fully connected, comma-delimited no-space list\
                                            [station, f_engine]", dest=full_req, default='station,f_engine')
    parser.add_argument('--update', help="Update part number records.  Format hpn0:[rev0]:col0:val0, \
                                          [hpn1:[rev1]]col1:val1...  [None]", default=None)
    parser.add_argument('--show-levels', help="Show power levels if enabled (and able) [False]", dest='show_levels', action='store_true')
    parser.add_argument('--levels-testing', help="Set to test filename if correlator levels not accessible - keep False \
                                                  to use actual correlator [False]", dest='levels_testing', default=False)
    parser.add_argument('--add-new-part', help="Flag to allow update to add a new record.  [False]", dest='add_new_part', action='store_true')
    
    cm_utils.add_verbosity_args(parser)
    cm_utils.add_date_time_args(parser)

    args = parser.parse_args()

    # Prep args
    if args.hpn:
        args.hpn = args.hpn.upper()
    if args.connection:
        args.connection = args.connection.upper()
    if args.mapr:
        args.mapr = args.mapr.upper()
    args.revision = args.revision.upper()
    date_query = cm_utils._get_astropytime(args.date,args.time)

    if type(args.levels_testing) == str:
        if args.levels_testing.lower() == 'none' or args.levels_testing.lower() == 'false':
            args.levels_testing = False
        elif args.levels_testing == 'levels.tst':
            args.levels_testing = os.path.join(mc.test_data_path, 'levels.tst')

    state_args = {'verbosity':args.verbosity.lower(),
                  'mapr_cols':args.mapr_cols.lower(),
                  'show_levels':args.show_levels,
                  'show_state':args.show_state,
                  'levels_testing':args.levels_testing}

    # Execute script
    db = mc.connect_to_mc_db(args)
    session = db.sessionmaker()

    handling = cm_handling.Handling(session)

    if args.hpn:
        part_dossier = handling.get_part_dossier(hpn=args.hpn, rev=args.revision,
                                                 at_date=date_query, exact_match=args.exact_match)
        handling.show_parts(part_dossier, state_args)

    if args.connection:
        connection_dossier = handling.get_connection_dossier(
                                      hpn=args.connection, rev=args.revision, port=args.specify_port,
                                      at_date=date_query, exact_match=args.exact_match)
        already_shown = handling.show_connections(connection_dossier, state_args)
        handling.show_other_connections(connection_dossier, already_shown)

    if args.mapr:
        from hera_mc import cm_hookup
        hookup = cm_hookup.Hookup(session)
        hookup_dict = hookup.get_hookup(hpn=args.mapr, rev=args.revision, port=args.specify_port,
                                        at_date=date_query, state_args=state_args, exact_match=args.exact_match)
        hookup.show_hookup(hookup_dict, args.mapr_cols, args.show_levels)

    if args.hptype:
        part_type_dict = handling.get_part_types(date_query, show_hptype=True)

    if args.show_rev and args.hpn is not None:
        rev_ret = cm_handling.cmpr.get_revisions_of_type(args.hpn, args.revision, date_query, session)
        cm_handling.cmpr.show_revisions(rev_ret)

    if args.check_rev is not None and args.hpn is not None:
        r = cm_handling.cmpr.check_rev(args.hpn, args.revision, args.check_rev, date_query, session)
        rrr = '' if r else ' not'
        print("{} rev {} is{} {}".format(args.hpn, args.revision, rrr, args.check_rev))

    if args.check_part_overlap and args.hpn is not None:
        cm_handling.cmpr.check_part_for_overlapping_revisions(args.hpn, session)

    if args.update:
        you_are_sure = cm_utils._query_yn("Warning:  Update is best done via a script -- are you sure you want to do this? ", 'n')
        if you_are_sure:
            part_connect.update(args, data)
