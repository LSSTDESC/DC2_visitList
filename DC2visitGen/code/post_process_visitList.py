import numpy as np
import pandas as pd
import os
import time
import lsst.sims.maf.db as db
import lsst.sims.maf

__all__ = ['post_process_visit_lists']

def post_process_visit_lists(dir_to_readfrom, wfd_filename, uddf_filename, base_filetag, outDir,
                             saveData=True, nVisits=None, group_by_year=False,
                             dbpath='/global/cscratch1/sd/awan/dbs_old_unzipped/minion_1016_desc_dithered_v3.db'):
    """

    The goal here is to take the all-band visit lists produced by DC2_visitListCode, separate them by band
    and save the obsHistIDs and expMJD corresponding to all the visits in the given band.

    Essentially following https://github.com/LSSTDESC/DC2-production/blob/master/Notebooks/survey_design_visit_lists.ipynb

    HOWEVER, Run 1.1 uDDF per-band production code include grouping by night, out of which the visits with the minimum airmass
    were chosen. Since all the visits need to be simulated for Run 2 and not just a subset, the uDDF lists are created the same
    way as for WFD: the visits are only grouped by band and ordered by expMJD.

    """
    startTime = time.time()
    print('Working with lsst.sims.maf.__version__: %s\n'%lsst.sims.maf.__version__)

    # create a dictionary to hold hold all-band visit lists
    visit_files = {}
    if wfd_filename is not None:
        visit_files['WFD'] = pd.read_csv('%s/visitLists/%s'%(dir_to_readfrom, wfd_filename), index_col='obsHistID')
    if uddf_filename is not None:
        visit_files['uDDF'] = pd.read_csv('%s/visitLists/%s'%(dir_to_readfrom, uddf_filename), index_col='obsHistID')
    if len(visit_files.keys())==0: # i.e. both uddf_filename, wfd_filename are None
        raise ValueError('Must provide at least one of the two: wfd_filename or uddf_filename')

    # read in the columns from the full database
    opsdb = db.OpsimDatabase(dbpath)
    colnames = ['obsHistID', 'expMJD', 'night']
    simdata = opsdb.fetchMetricData(colnames=colnames, sqlconstraint=None, groupBy='expMJD')

    # need obsHistID as an index (easier to match stuff) and as a column itself (easier to save things)
    temp = {}
    for key in colnames:
        if key!='obsHistID':
            temp[key] = simdata[key]
    simdata_pd = pd.DataFrame(temp, index=simdata['obsHistID'])
    simdata_pd.index.name = 'obsHistID'
    simdata_pd['obsHistID'] = simdata_pd.index

    to_return = {}
    # loop over WFD, DDF and save files
    for surveytag in visit_files:
        to_return[surveytag] = {}
        tot = 0   # to track how many visits are save across all the bands
        print('## Working with %s\n'%surveytag)
        print('All-band array: shape = %s\n'%(np.shape(visit_files[surveytag]),))

        # add the expDate column to the data dframe
        # also, check if need to limit the number of visits to get
        if nVisits is not None:
            df = visit_files[surveytag].join(simdata_pd).sort_values(by='expMJD').iloc[:nVisits[surveytag]]
        else:
            df = visit_files[surveytag].join(simdata_pd).sort_values(by='expMJD')

        if saveData: print('Outdir: %s\n'%outDir)
        # group by band and save obsHistID and expMJD
        groups = df.groupby('band')
        for band in groups.groups.keys():
            print('------------------------------------------------------------------------')
            print('Working with %s-band'%band)

            if group_by_year:
                to_return[surveytag][band] = {}
                subset = groups.get_group(band)
                print('%s visits for %s-band.'%(len(subset), band))
                subset['year'] = [int(np.floor(f/365.25))+1 for f in subset['night']]

                groups_yr = subset.groupby('year')

                for yr in groups_yr.groups.keys():
                    subset_yr = groups_yr.get_group(yr)[['obsHistID', 'expMJD']]
                    print('%s visits for year %s.'%(len(subset_yr), yr))
                    tot += len(subset_yr)

                    if saveData:
                        # save the file
                        filename = '%s_%s-band_Y%s_%svisits.txt'%(base_filetag, band, yr, surveytag)
                        subset_yr.to_csv('%s/%s'%(outDir, filename), index=False, sep=' ', header=['obsHistID', 'expMJD'])
                        print('\nSaved %s.\n'%(filename))

                    to_return[surveytag][band][yr] = subset_yr

            else:
                subset = groups.get_group(band)[['obsHistID', 'expMJD']]
                print('%s visits for %s-band.'%(len(subset), band))
                tot += len(subset)
                if saveData:
                    # save the file
                    filename = '%s_%s-band_%svisits.txt'%(base_filetag, band, surveytag)
                    subset.to_csv('%s/%s'%(outDir, filename), index=False, sep=' ', header=['obsHistID', 'expMJD'])
                    print('\nSaved %s\n'%(filename))

                to_return[surveytag][band] = subset

        print('Total %s %s visits saved.\n'%(tot, surveytag))

    print('All done. Time taken: %.2f s'%(time.time()-startTime))

    return to_return