#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright 2018 the HERA Collaboration
# Licensed under the 2-clause BSD license.

"""
Script to handle installing a new station into system.
"""

from __future__ import absolute_import, division, print_function

import os.path
import six
from hera_mc import mc, geo_location, cm_utils, part_connect, geo_handling

region = {'herahexw': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                       23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46,
                       50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75,
                       81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108,
                       116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145],
          'herahexe': [22, 34, 35, 47, 48, 49, 61, 62, 63, 64, 76, 77, 76, 78, 80, 92, 93, 94, 95, 96, 97,
                       109, 110, 111, 112, 113, 114, 115, 127, 128, 129, 130, 131, 132, 133, 134, 146, 147, 148, 149, 150, 151, 152, 153, 154,
                       166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 187, 188, 189, 190, 191, 192, 193, 194, 195,
                       207, 208, 209, 210, 211, 212, 213, 214, 226, 227, 228, 229, 230, 231, 232, 244, 245, 246, 247, 248, 249,
                       261, 262, 263, 264, 265, 277, 278, 279, 280, 292, 293, 294, 306, 307, 319],
          'herahexn': [155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186,
                       196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225,
                       233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260,
                       266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291,
                       295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318],
          'heraringa': [325, 326, 327, 330, 331, 334, 335, 338, 339, 342, 343, 344],
          'heraringb': [320, 321, 322, 323, 324, 328, 329, 332, 333, 336, 337, 340, 341, 345, 346, 347, 348, 349]}


def read_nodes():
    node_coord_file_name = os.path.join(mc.data_path, 'nodes.txt')
    default_elevation = 1050.0
    nodes = {}
    with open(node_coord_file_name, 'r') as fp:
        for line in fp:
            node_num = int(line.split(':')[0])
            node_E = float(line.split(':')[1].split(',')[0])
            node_N = float(line.split(':')[1].split(',')[1])
            ants = line.split(':')[2].split(',')
            ants = [int(x) for x in ants]
            nodes[node_num] = {'E': node_E, 'N': node_N, 'elevation': default_elevation, 'ants': ants}
    return nodes


def read_antennas():
    antenna_coord_file_name = os.path.join(mc.data_path, 'HERA_350.txt')
    antennas = {}
    with open(antenna_coord_file_name, 'r') as fp:
        for line in fp:
            data = line.split()
            coords = [data[0], float(data[1]), float(data[2]), float(data[3])]
            antennas[coords[0]] = {'E': coords[1], 'N': coords[2], 'elevation': coords[3]}
    return antennas


def query_geo_information(args):
    """
    Gets geo_location information from user
    """
    if args.easting is None:
        args.easting = float(raw_input('Easting:  '))
    if args.northing is None:
        args.northing = float(raw_input('Northing:  '))
    if args.elevation is None:
        args.elevation = float(raw_input('Elevation:  '))
    args.datum = cm_utils.query_default('datum', args)
    args.tile = cm_utils.query_default('tile', args)
    if args.station_type_name is None:
        args.station_type_name = raw_input('Station type name: ')
    args.date = cm_utils.query_default('date', args)
    return args


def entry_OK_to_add(session, station_name):
    OK = True
    h = geo_handling.Handling(session)
    if h.is_in_database(station_name):
        print(station_name, ' already present.')
        OK = False
    h.close()
    return OK


def add_entry_to_geo_location(session, args):
    # NotNull
    sname = args.station_name
    dt = cm_utils.get_astropytime(args.date, args.time)
    data = [[sname, 'station_name', sname],
            [sname, 'station_type_name', args.station_type_name],
            [sname, 'created_gpstime', dt.gps]]
    # Other
    if args.datum:
        data.append([sname, 'datum', args.datum])
    if args.tile:
        data.append([sname, 'tile', args.tile])
    if args.northing:
        data.append([sname, 'northing', args.northing])
    if args.easting:
        data.append([sname, 'easting', args.easting])
    if args.elevation:
        data.append([sname, 'elevation', args.elevation])
    geo_location.update(session, data, args.add_new_geo)


def add_entry_to_parts(session, args):
    # NotNull
    hpn = args.station_name
    rev = 'A'
    dt = cm_utils.get_astropytime(args.date, args.time)
    data = [[hpn, rev, 'hpn', hpn],
            [hpn, rev, 'hpn_rev', rev],
            [hpn, rev, 'hptype', 'station'],
            [hpn, rev, 'manufacturer_number', hpn],
            [hpn, rev, 'start_gpstime', dt.gps]]
    part_connect.update_part(session, data, args.add_new_part)


if __name__ == '__main__':
    parser = mc.get_mc_argument_parser()
    parser.add_argument('station_name', help="Name of station (HH# for hera, ND# for node).")
    parser.add_argument('-e', '--easting', help="Easting of new station.", default=None)
    parser.add_argument('-n', '--northing', help="Northing of new station", default=None)
    parser.add_argument('-z', '--elevation', help="Elevation of new station", default=None)
    cm_utils.add_date_time_args(parser)
    parser.add_argument('--station_type_name', help="Station category name", default=None)
    parser.add_argument('--datum', help="Datum of UTM [WGS84]", default='WGS84')
    parser.add_argument('--tile', help="UTM tile [34J]", default='34J')
    cm_utils.add_verbosity_args(parser)
    parser.add_argument('--add_new_geo', help="Flag to allow update to add a new "
                        "record.  [True]", action='store_false')
    parser.add_argument('--add_new_part', help="Flag to allow update to add a new "
                        "record.  [True]", action='store_false')

    args = parser.parse_args()
    args.verbosity = args.verbosity.lower()
    args.station_name = args.station_name.upper()
    if args.station_name[:2] in ['HH', 'HA', 'HB']:
        antenna = read_antennas()
        if args.station_name not in antenna:
            raise ValueError("{} antenna not found.".format(args.station_name))
        args.easting = antenna[args.station_name]['E']
        args.northing = antenna[args.station_name]['N']
        args.elevation = antenna[args.station_name]['elevation']
        ant_num = int(args.station_name[2:])
        for r, v in six.iteritems(region):
            if ant_num in v:
                args.station_type_name = r
                break
    elif args.station_name[:2] == 'ND':
        node = read_nodes()
        node_num = int(args.station_name[2:])
        if node_num not in node:
            raise ValueError("{} node not found.".format(args.station_name))
        args.easting = node[node_num]['E']
        args.northing = node[node_num]['N']
        args.elevation = node[node_num]['elevation']
        args.station_type_name = 'node'
    else:
        args = query_geo_information(args)

    db = mc.connect_to_mc_db(args)
    session = db.sessionmaker()

    if entry_OK_to_add(session, args.station_name):
        cm_utils.log('add_station', args=args)
        add_entry_to_geo_location(session, args)
        add_entry_to_parts(session, args)
