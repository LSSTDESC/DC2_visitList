# visit_filter.py 10 Sept 2018
# Reads Humna's DC2 visit lists, removes the visits that overlap the DDF or have vSkyBright < 18.
# writes filtered visits to separate files

import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect('/global/projecta/projectdirs/lsst/groups/SSim/DC2/minion_1016_desc_dithered_v4.db')

ra_min = np.radians(49.92)
ra_max = np.radians(73.79)
dec_min = np.radians(-44.33)
dec_max = np.radians(-27.25)

query = 'select * from summary where fieldRA>{} and fieldRA<{} and fieldDec>{} and fieldDec<{}'.format(ra_min, ra_max, dec_min, dec_max)

df = pd.read_sql(query, conn)

inroot = '../../DC2visitGen/DC2_Run2_Visits_nside1024/visitLists/'
outroot = inroot + 'per_band_lists_WFD_filtered/'
vsb_cut = 18  # maximum accepted vSkyBright

for band in 'ugrizy':
    wfd = {}
    wfd_overlap = {}
    wfd_bright = {}
    # read the WFD file contents
    WFD_file = inroot + 'per_band_lists/DC2_Run2_' + band + '-band_WFDvisits.txt'
    print('Processing:  ' + WFD_file)
    with open(WFD_file) as f:
        content = f.readlines()
    for line in content:
        pieces = line.split()
        wfd[pieces[0]] = pieces[1]

    # look up the bright sky visits
    bright = df.query("filter == '{}' and vSkyBright <{}".format(band,vsb_cut))
    bright_ids = np.array(bright['obsHistID'])
    # remove the visits that have vSkyBright < skyBright_limit
    count = 0
    for bad in bright_ids:
        if str(bad) in wfd.keys():
            wfd_bright[bad] = wfd[str(bad)]  # nb, not str for wfd_bright, so can sort in numerical order
            del wfd[str(bad)]
            count += 1

    print('# bright visits removed:  %s' % count)

    # construct the name of the DDF overlap file
    Overlap_file = inroot + 'per_band_lists_WFD_subset_overlap_DDF/DC2_Run2_' + band + '-band_WFDvisits.txt'

    # read that file
    count = 0
    with open(Overlap_file) as f:
        content = f.readlines()
    # remove the entries from the WFD file contents
    for line in content:
        pieces = line.split()
        if pieces[0] in wfd.keys():
            count += 1
            del wfd[pieces[0]]
            wfd_overlap[pieces[0]] = pieces[1]
    print('# DDF overlaps removed: %s' % count)

    # construct the output file name (good visits)
    outfile = outroot + 'DC2_Run2_' + band + '-band_WFDvisits_noDDF_noBright.txt'
    # write the file
    with open(outfile, "w") as f:
        f.write('obsHistID expMJD\n')
        for id in wfd.keys():
            outstr = id + ' ' + wfd[id] + '\n'
            f.write(outstr)

    # construct the output file name (bright visits)
    outfile = outroot + 'DC2_Run2_' + band + '-band_WFDvisits_tooBright.txt'
    # write the file
    with open(outfile, "w") as f:
        f.write('obsHistID expMJD\n')
        for id in sorted(wfd_bright):  #.keys():
            outstr = str(id) + ' ' + wfd_bright[id] + '\n'
            f.write(outstr)

    # construct the output file name (DDF not bright visits)
    outfile = outroot + 'DC2_Run2_' + band + '-band_WFDvisits_DDF_notBright.txt'
    # write the file
    with open(outfile, "w") as f:
        for id in wfd_overlap.keys():
            outstr = id + ' ' + wfd_overlap[id] + '\n'
            f.write(outstr)
