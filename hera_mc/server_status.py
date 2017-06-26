# -*- mode: python; coding: utf-8 -*-
# Copyright 2017 the HERA Collaboration
# Licensed under the 2-clause BSD license.

"""
Common server_status table

The columns in this module are documented in docs/mc_definition.tex,
the documentation needs to be kept up to date with any changes.
"""
from math import floor
from astropy.time import Time
from sqlalchemy import Column, Integer, String, Float, BigInteger
from . import MCDeclarativeBase, DEFAULT_GPS_TOL, DEFAULT_DAY_TOL


class ServerStatus(MCDeclarativeBase):
    """
    Definition of server_status table.

    hostname: name of server (String). Part of primary_key
    mc_time: time report received by M&C in floor(gps seconds) (BigInteger). Part of primary_key
    ip_address: IP address of server (String)
    mc_system_timediff: difference between M&C time and time report sent by server in seconds (Float)
    num_cores: number of cores on server (Integer)
    cpu_load_pct: CPU load percent = total load / num_cores, 5 min average (Float)
    uptime_days: server uptime in decimal days (Float)
    memory_used_pct: Percent of memory used, 5 min average (Float)
    memory_size_gb: Amount of memory on server in GB (Float)
    disk_space_pct: Percent of disk used (Float)
    disk_size_gb: Amount of disk space on server in GB (Float)
    network_bandwidth_mbs: Network bandwidth in MB/s, 5 min average. Can be null if not applicable
    """
    __abstract__ = True
    hostname = Column(String(32), primary_key=True)
    mc_time = Column(BigInteger, primary_key=True)
    ip_address = Column(String(32), nullable=False)
    mc_system_timediff = Column(Float, nullable=False)
    num_cores = Column(Integer, nullable=False)
    cpu_load_pct = Column(Float, nullable=False)
    uptime_days = Column(Float, nullable=False)
    memory_used_pct = Column(Float, nullable=False)
    memory_size_gb = Column(Float, nullable=False)
    disk_space_pct = Column(Float, nullable=False)
    disk_size_gb = Column(Float, nullable=False)
    network_bandwidth_mbs = Column(Float)

    tols = {'mc_system_timediff': DEFAULT_GPS_TOL,
            'uptime_days': DEFAULT_DAY_TOL}

    @classmethod
    def create(cls, db_time, hostname, ip_address, system_time, num_cores,
               cpu_load_pct, uptime_days, memory_used_pct, memory_size_gb,
               disk_space_pct, disk_size_gb, network_bandwidth_mbs=None):
        """
        Create a new server_status object.

        Parameters:
        ------------
        db_time: astropy time object
            astropy time object based on a timestamp from the database.
            Usually generated from MCSession.get_current_db_time()
        hostname: string
            name of server
        ip_address: string
            IP address of server
        system_time: astropy time object
            time report sent by server
        num_cores: integer
            number of cores on server
        cpu_load_pct: float
            CPU load percent = total load / num_cores, 5 min average
        uptime_days: float
            server uptime in decimal days
        memory_used_pct: float
            Percent of memory used, 5 min average
        memory_size_gb: float
            Amount of memory on server in GB
        disk_space_pct: float
            Percent of disk used
        disk_size_gb: float
            Amount of disk space on server in GB
        network_bandwidth_mbs: float
            Network bandwidth in MB/s, 5 min average. Can be null if not applicable
        """
        if not isinstance(db_time, Time):
            raise ValueError('db_time must be an astropy Time object')
        mc_time = floor(db_time.gps)

        if not isinstance(system_time, Time):
            raise ValueError('system_time must be an astropy Time object')
        mc_system_timediff = db_time.gps - system_time.gps

        return cls(hostname=hostname, mc_time=mc_time, ip_address=ip_address,
                   mc_system_timediff=mc_system_timediff, num_cores=num_cores,
                   cpu_load_pct=cpu_load_pct, uptime_days=uptime_days,
                   memory_used_pct=memory_used_pct, memory_size_gb=memory_size_gb,
                   disk_space_pct=disk_space_pct, disk_size_gb=disk_size_gb,
                   network_bandwidth_mbs=network_bandwidth_mbs)