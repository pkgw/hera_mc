#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright 2016 the HERA Collaboration
# Licensed under the 2-clause BSD license.

"""
Script to show cm_log_file.  Extremely simplified here - can fancify later.
"""

from __future__ import absolute_import, division, print_function

from hera_mc import mc
import sys
import os.path


if __name__ == '__main__':
    parser = mc.get_mc_argument_parser()
    parser.add_argument('-v', '--verbosity', help="Set verbosity. [h].", choices=['l', 'm', 'h'], default="h")
    args = parser.parse_args()
    args.verbosity = args.verbosity.lower()

    with open(mc.cm_log_file,'r') as log_file:
        for line in log_file:
            print(line.strip())