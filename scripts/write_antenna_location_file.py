#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright 2016 the HERA Collaboration
# Licensed under the 2-clause BSD license.

"""
Script to write out antenna locations for use in cal files.
"""
import pandas as pd
from hera_mc import mc, geo_handling
import datetime

parser = mc.get_mc_argument_parser()
parser.add_argument('--file', help="file name to save antenna locations to",
                    default='hera_ant_locs_' + datetime.date.today().strftime("%m_%d_%Y") + '.csv')
args = parser.parse_args()
filename = args.file
db = mc.connect_to_mc_db(args)

locations = geo_handling.get_all_locations(args)
cofa_loc = geo_handling.cofa()
locations.append({'station_name': cofa_loc.station_name,
                  'station_type': cofa_loc.station_type_name,
                  'longitude': cofa_loc.lon,
                  'latitude': cofa_loc.lat,
                  'elevation': cofa_loc.elevation,
                  'antenna_number': None,
                  'start_date': cofa_loc.created_date,
                  'stop_date': None})
df = pd.DataFrame(locations)
df = df[['station_name', 'station_type', 'longitude', 'latitude', 'elevation',
        'antenna_number', 'start_date', 'stop_date']]
df.to_csv(filename, index=False)
