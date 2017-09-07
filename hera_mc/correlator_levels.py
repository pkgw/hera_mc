# This requires that the rails server is running:
# $ cd /home/davidm/local/src/rails-paper
# $ rails server --daemon
# (http://herawiki.berkeley.edu/doku.php/correlator.operations)

from __future__ import print_function
import urllib2

paper_network = True


def get_levels(pf_input, testing):
    """
    This assumes the f_engine name structure of 'DF<int=pf_chassis><letter=input_row><int=input_col>'
    """
    pf_in__to__file_col = {'A1': 0, 'A2': 1, 'A3': 2, 'A4': 3,
                           'B1': 4, 'B2': 5, 'B3': 6, 'B4': 7,
                           'C1': 8, 'C2': 9, 'C3': 10, 'C4': 11,
                           'D1': 12, 'D2': 13, 'D3': 14, 'D4': 15,
                           'E1': 16, 'E2': 17, 'E3': 18, 'E4': 19,
                           'F1': 20, 'F2': 21, 'F3': 22, 'F4': 23,
                           'G1': 24, 'G2': 25, 'G3': 26, 'G4': 27,
                           'H1': 28, 'H2': 29, 'H3': 30, 'H4': 31}
    default_levels_filename = '__levels.tmp'
    live_values = __get_current_levels_from_url(default_levels_filename)
    if live_values:
        levels_filename = default_levels_filename
    else:
        print("\nNOT LIVE CORRELATOR VALUES:  Reading from default test file.")
        levels_filename = testing

    levels = __read_levels_file(levels_filename)
    if type(pf_input) is not list:
        pf_input = [pf_input]
    pf_levels = []
    for pf in pf_input:
        try:
            pf_chassis = 'F' + str(pf[-3])
        except ValueError:
            print("Not standard f_engine naming format (pf chassis)", pf)
            continue
        pf_rowcol_designator = pf[-2:]
        try:
            level_col = pf_in__to__file_col[pf_rowcol_designator]
        except KeyError:
            print("Not standard f_engine naming format (pf input)", pf)
            continue
        if levels is not None:
            pf_levels.append(levels[pf_chassis][level_col])
        else:
            pf_levels.append('-')
    return pf_levels


def __read_levels_file(name):
    try:
        lfp = open(name, 'r')
    except IOError:
        print('Warning:', name, 'not found.')
        return None
    levels = {}
    for line in lfp:
        d = line.split()
        pf = d[0][1:].upper()
        levels[pf] = d[2:]
    lfp.close()
    return levels


def __get_current_levels_from_url(name, timeout=5):
    try:
        if paper_network:
            url = urllib2.urlopen('http://10.0.1.1:3000/instruments/psa256/levels.txt', timeout=timeout)
        else:
            url = urllib2.urlopen('http://10.0.1.1:3000/instruments/psa256/levels.txt', timeout=timeout)
        levels_url = url.read()
        fp = open(name, 'w')
        fp.write(levels_url)
        fp.close()
        return True
    except urllib2.URLError:
        return False
