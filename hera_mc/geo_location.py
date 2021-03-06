# -*- mode: python; coding: utf-8 -*-
# Copyright 2016 the HERA Collaboration
# Licensed under the 2-clause BSD license.

"""Keeping track of geo-located stations.

"""

from __future__ import absolute_import, division, print_function

import os
import socket
import sys
import copy
from astropy.time import Time
from sqlalchemy import Column, Float, Integer, String, BigInteger, ForeignKey, func

from . import MCDeclarativeBase, NotNull
from . import mc, part_connect, cm_utils


class StationType(MCDeclarativeBase):
    """
    A table to track/denote station type data categories in various ways

    station_type_name: Name of type class, Primary_key
        Note that prefix is not in the primary_key, so there can be multiple
        prefixes per type_name.
    prefix: String prefix to station type, elements of which are typically
            characterized by <prefix><int>. Comma-delimit list if more than one.
    description: Short description of station type.
    plot_marker: matplotlib marker type to use
    """
    __tablename__ = 'station_type'

    station_type_name = Column(String(64), primary_key=True)
    prefix = NotNull(String(64))
    description = Column(String(64))
    plot_marker = Column(String(64))

    def __repr__(self):
        return '<subarray {self.station_type_name}: prefix={self.prefix} description={self.description} marker={self.plot_marker}>'.format(self=self)


class GeoLocation(MCDeclarativeBase):
    """A table logging stations within HERA.

    station_name: Colloquial name of station (which is a unique location on the ground).
        This one shouldn't change. Primary_key
    station_type_name: Name of station type of which it is a member.
        Should match prefix per station_type table.
    datum: Datum of the geoid.
    tile: UTM tile
    northing: Northing coordinate in m
    easting: Easting coordinate in m
    elevation: Elevation in m
    created_gpstime: The date when the station assigned by project.
    """
    __tablename__ = 'geo_location'

    station_name = Column(String(64), primary_key=True)
    station_type_name = Column(String(64), ForeignKey(StationType.station_type_name),
                               nullable=False)
    datum = Column(String(64))
    tile = Column(String(64))
    northing = Column(Float(precision='53'))
    easting = Column(Float(precision='53'))
    elevation = Column(Float)
    created_gpstime = NotNull(BigInteger)

    def gps2Time(self):
        self.created_date = Time(self.created_gpstime, format='gps')

    def geo(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'station_name':
                value = value.upper()
            setattr(self, key, value)

    def __repr__(self):
        return '<station_name={self.station_name} station_type={self.station_type_name} \
        northing={self.northing} easting={self.easting} \
        elevation={self.elevation}>'.format(self=self)


def update(session=None, data=None, add_new_geo=False):
    """
    update the database given a station_name and station_number with columns/values
        and provides some checking.
    use with caution -- should usually use in a script which will do datetime
        primary key etc

    Parameters:
    ------------
    session: session on current database. If session is None, a new session
             on the default database is created and used.
    data:  [[station_name0,column0,value0],[...]]
           where
                station_nameN:  station_name (starts with char)
                values:  corresponding list of values
    add_new_geo:  boolean to allow a new entry to be made.
    """

    data_dict = format_check_update_request(data)
    if data_dict is None:
        print('Error: invalid update -- doing nothing.')
        return False

    close_session_when_done = False
    if session is None:
        db = mc.connect_mc_db()
        session = db.sessionmaker()
        close_session_when_done = True

    for station_name in data_dict.keys():
        geo_rec = session.query(GeoLocation).filter(func.upper(GeoLocation.station_name) == station_name.upper())
        num_rec = geo_rec.count()
        make_update = False
        if num_rec == 0:
            if add_new_geo:
                gr = GeoLocation()
                make_update = True
            else:
                print("Error: ", station_name, "does not exist and add_new_geo not enabled.")
        elif num_rec == 1:
            if add_new_geo:
                print("Error: ", station_name, "exists and and_new_geo is enabled.")
            else:
                gr = geo_rec.first()
                make_update = True
        else:
            print("Error:  more than one of ", station_name,
                  " exists (which should not happen).")
        if make_update:
            for d in data_dict[station_name]:
                try:
                    setattr(gr, d[1], d[2])
                except AttributeError:
                    print(d[1], 'does not exist as a field')
                    continue
            session.add(gr)
            session.commit()
    cm_utils.log('geo_location update', data_dict=data_dict)
    if close_session_when_done:
        session.close()

    return True


def format_check_update_request(request):
    """
    parses the update request

    return dictionary

    Parameters:
    ------------
    request:  station_name0:column0:value0, [station_name1:]column1:value1, [...] or list
        station_nameN: first entry must have the station_name,
                       if it does not then propagate first station_name but
                       can't restart 3 then 2
        columnN:  name of geo_location column
        valueN:  corresponding new value
    """
    if request is None:
        return None
    data = {}
    if type(request) == str:
        tmp = request.split(',')
        data_to_proc = []
        for d in tmp:
            data_to_proc.append(d.split(':'))
    else:
        data_to_proc = request
    if len(data_to_proc[0]) == 3:
        station_name0 = data_to_proc[0][0]
        for d in data_to_proc:
            if len(d) == 3:
                pass
            elif len(d) == 2:
                d.insert(0, station_name0)
            else:
                print('Invalid format for update request.')
                continue
            if d[0] in data.keys():
                data[d[0]].append(d)
            else:
                data[d[0]] = [d]
    else:
        print('Invalid parse request - need 3 parameters for at least first one.')
        data = None
    return data
