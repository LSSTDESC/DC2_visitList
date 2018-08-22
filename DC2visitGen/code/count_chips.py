import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import healpy as hp
import pandas as pd
import time
import pickle

import lsst.sims.maf.db as db
import lsst.sims.maf.slicers as slicers
from lsst.obs.lsstSim import LsstSimMapper
from lsst.sims.utils import ObservationMetaData
from lsst.sims.utils import _getRotSkyPos

from lsst.sims.coordUtils import chipNameFromRaDec

############################################################################################################
dbpath = '/global/cscratch1/sd/awan/dbs_old_unzipped/minion_1016_desc_dithered_v3.db'
pointingRACol = 'descDitheredRA'
pointingDecCol = 'descDitheredDec'
rotTelCol = 'descDitheredRotTelPos'
surveyRegionTag = 'WFD'

nside = 1024

output_path = '/global/homes/a/awan/LSST/lsstRepos/DC2_visitList/DC2visitGen/DC2_Run2_Visits_nside1024/'
pixel_path = '%sregionPixels/DC2RegionPixels_minion1016_v3_%svisits_nside%s_%svisitsIn%s.csv'%(output_path, surveyRegionTag, nside,
                                                                                               surveyRegionTag, surveyRegionTag)
visits_path = '%svisitLists/DC2VisitList_minion1016_v3_%svisits_nside%s_%svisitsIn%s.csv'%(output_path, surveyRegionTag, nside,
                                                                                           surveyRegionTag, surveyRegionTag)


############################################################################################################
print('\nConnecting to the database ... ')
print(dbpath)
opsdb = db.OpsimDatabase(dbpath)
propIds, propTags = opsdb.fetchPropInfo()
sqlconstraint  = opsdb.createSQLWhere(surveyRegionTag, propTags)
print('sqlconstraint: %s'%sqlconstraint)
colnames = ['fieldID', 'expMJD', 'obsHistID', pointingRACol, pointingDecCol, rotTelCol]
print('Reading in: %s'%colnames)
simdata = opsdb.fetchMetricData(colnames, sqlconstraint)

#----------------------------------------------------------------------------------------------
print('\nReading in regionPixels ... ')
regionPixels = pd.read_csv(pixel_path)
regionPixels = np.array(regionPixels['regionPixels'])
totPixels = len(regionPixels)
print('%s pixels to consider.'%totPixels)

#----------------------------------------------------------------------------------------------
print('\nSetting up the slicer ... ')
hpSlicer = slicers.HealpixSlicer(nside=nside, latLonDeg=opsdb.raDecInDeg, lonCol=pointingRACol, latCol=pointingDecCol)
hpSlicer.setupSlicer(simdata)    # slice data: know which pixels are observed in which visit

#----------------------------------------------------------------------------------------------
print('\nSetting up the camera ... ')
camera = LsstSimMapper().camera
chipNames, obsIDs, fIDs, pixNums= [], [], [], []

#----------------------------------------------------------------------------------------------
print('\nStarting the chip count ... ')
prevPercent = 0.
startTime = time.time()
for p, pixel in enumerate(regionPixels):  # run over all the pixels in the region
    pixRA, pixDec = hpSlicer._pix2radec(pixel)    # radians returned
    indObsInPixel = hpSlicer._sliceSimData(pixel)   # indices in simData for when an observation
                                                    # happened in this pixel

    for index in indObsInPixel['idxs']:
        # get data from simdata for identifying each visit
        obsID = simdata[index]['obsHistID']
        fID = simdata[index]['fieldID']

        # for chip finding
        pointingRA = simdata[index][pointingRACol] # radians
        pointingDec = simdata[index][pointingDecCol] # radians
        rotTelPos = simdata[index][rotTelCol] # radians
        expMJD = simdata[index]['expMJD']

        rotSkyPos = _getRotSkyPos(pointingRA, pointingDec, ObservationMetaData(mjd=expMJD), rotTelPos)
        
        # set up for the finding the chips
        if not opsdb.raDecInDeg:
            obs = ObservationMetaData(pointingRA=np.degrees(pointingRA), pointingDec=np.degrees(pointingDec),
                                      rotSkyPos=np.degrees(rotSkyPos), mjd=expMJD)
            
        chipsInVisit = chipNameFromRaDec(np.degrees(pixRA), np.degrees(pixDec),
                                         camera=camera, obs_metadata=obs)
        if chipsInVisit is not None:
            if not (chipsInVisit.__contains__('A')) and not (chipsInVisit.__contains__('B')): # no wavefront sensors
                obsIDs.append(obsID)
                chipNames.append(chipsInVisit)
                fIDs.append(fID)
                pixNums.append(pixel)

    percentDone = 100.*(p+1)/totPixels
    delPercent = percentDone-prevPercent
    if (delPercent>1):
        print('%f%% pixels done\nTime passed (min): %f\n'%(percentDone, (time.time()-startTime)/60.))
        prevPercent = percentDone
    #if (percentDone>1.):
    #    break
print('\nAll done.\nTime passed (min): %f\n'%((time.time()-startTime)/60.))

#----------------------------------------------------------------------------------------------
obsIDs, fIDs, chipNames, pixNums = np.array(obsIDs), np.array(fIDs), np.array(chipNames), np.array(pixNums)
print('Unique obsHistIDs: %d \n## Unique chipNames: %d \n'%(len(np.unique(obsIDs)), len(np.unique(chipNames))))

#  get rid of repeated entries; consolidate the data from unique observations.
print('Consolidating the data ... ')
obsIDsList, fIDsList, chipNamesList, pixNumsList = [], [], [], []
for obs in np.unique(obsIDs):
    obsIDsList.append(obs)
    ind= np.where(obsIDs==obs)[0]
    fIDsList.append(np.unique(fIDs[ind]))
    chipNamesList.append(np.unique(chipNames[ind]))
    pixNumsList.append(np.unique(pixNums[ind]))

# see how many chips are added by any given visit
numChips= []
for i in range(len(obsIDsList)):
    numChips.append(len(chipNamesList[i]))
    
print('Min, Max number of chips added by any given visit: %d, %s'%( min(numChips), max(numChips)))
print('Total number of chips (across all visits to be simulated): %d'%sum(numChips))

#----------------------------------------------------------------------------------------------
out = pd.read_csv(visits_path)
if np.array(out['obsHistID'])!=obsIDsList:
    print('\n##ObsIDs do not match.')
    plt.clf()
    plt.hist(out['obsHistID'], label='saved before', histtype='step')
    plt.hist(obsIDsList, label='calculated here', histtype='step')
    plt.xlabel('Bins of obsIDs')
    plt.ylabel('Counts')
    plt.legend()
    plt.show()
else:
    print('\nObsIDs match.')
#----------------------------------------------------------------------------------------------
# save the data
dataToSave = {'obsHistID': obsIDsList, 'fIDs': fIDsList, 'chipNames': chipNamesList}
filename = 'chipPerVisitData_%s_nside%s_%dNonWFChipsToSimulate.pickle'%(surveyRegionTag, nside, sum(numChips))
with open('%s/%s'%(output_path, filename), 'wb') as handle:
    pickle.dump(dataToSave, handle, protocol=pickle.HIGHEST_PROTOCOL)

print('\nSaved %s in %s\n'%(filename, output_path))
