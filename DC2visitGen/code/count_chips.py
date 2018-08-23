import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import healpy as hp
import pandas as pd
import time
import pickle
import datetime

import lsst.sims.maf
import lsst.sims.maf.db as db
import lsst.sims.maf.slicers as slicers
from lsst.obs.lsstSim import LsstSimMapper
from lsst.sims.utils import ObservationMetaData
from lsst.sims.utils import _getRotSkyPos

from lsst.sims.coordUtils import chipNameFromRaDec

########################################################################
from optparse import OptionParser
parser = OptionParser()
parser.add_option('-q', '--quiet',
                  action= 'store_false', dest= 'verbose', default=True,
                  help= 'Do not print stuff out')
parser.add_option('--nside', dest='nside',
                  help='HEALPix resolution parameter.',
                  default=1024)
parser.add_option('--surveyRegionTag', dest='surveyRegionTag',
                  help='Either WFD or DD',
                  default='WFD')
parser.add_option('--dataFolder', dest='dataFolder',
                  help='Folder name in DC2visitGen that contains the regionPixels and visitLists',
                  default='DC2_Run2_Visits_nside1024')

(options, args) = parser.parse_args()
verbose = options.verbose
nside = int(options.nside)
surveyRegionTag = options.surveyRegionTag
dataFolder = options.dataFolder

############################################################################################################
dbpath = '/global/cscratch1/sd/awan/dbs_old_unzipped/minion_1016_desc_dithered_v3.db'
pointingRACol = 'descDitheredRA'
pointingDecCol = 'descDitheredDec'
rotTelCol = 'descDitheredRotTelPos'

if surveyRegionTag=='DD':
    inRegionTag = 'uDD'
else:
    inRegionTag = surveyRegionTag
output_path = '/global/homes/a/awan/LSST/lsstRepos/DC2_visitList/DC2visitGen/%s/'%dataFolder
pixel_path = '%sregionPixels/DC2RegionPixels_minion1016_v3_%svisits_nside%s_%svisitsIn%s.csv'%(output_path, surveyRegionTag, nside,
                                                                                               surveyRegionTag, inRegionTag)
visits_path = '%svisitLists/DC2VisitList_minion1016_v3_%svisits_nside%s_%svisitsIn%s.csv'%(output_path, surveyRegionTag, nside,
                                                                                           surveyRegionTag, inRegionTag)
############################################################################################################
def add_update(update, readme, verbose):
    if verbose: print(update)
    return '%s\n%s'%(readme,update)

############################################################################################################
startTime_0 = time.time()
if verbose:
    print('Nside: %s\nsurveyRegionTag: %s\nData read in from %s'%(nside, surveyRegionTag, dataFolder))

readme = '##############################\n%s'%(datetime.date.isoformat(datetime.date.today()))
readme += '\nRunning with lsst.sims.maf.__version__: %s'%lsst.sims.maf.__version__
readme += '\n\ncount_chips run:\ndataFolder= %s'%dataFolder
readme += '\nnside: %s'%nside
readme += '\nsurveyRegionTag: %s'%surveyRegionTag
readme += '\ndbpath: %s'%dbpath
readme += '\n%s, %s, %s'%(pointingRACol, pointingDecCol, rotTelCol)

#----------------------------------------------------------------------------------------------
readme = add_update(update='\nConnecting to the database ... \n%s'%dbpath, readme=readme, verbose=verbose)

opsdb = db.OpsimDatabase(dbpath)
propIds, propTags = opsdb.fetchPropInfo()
sqlconstraint  = opsdb.createSQLWhere(surveyRegionTag, propTags)
readme = add_update(update='sqlconstraint: %s'%sqlconstraint, readme=readme, verbose=verbose)

colnames = ['fieldID', 'expMJD', 'obsHistID', pointingRACol, pointingDecCol, rotTelCol]
readme = add_update(update='Reading in: %s'%colnames, readme=readme, verbose=verbose)
simdata = opsdb.fetchMetricData(colnames, sqlconstraint)

#----------------------------------------------------------------------------------------------
readme = add_update(update='\nReading in regionPixels ... ', readme=readme, verbose=verbose)
regionPixels = pd.read_csv(pixel_path)
regionPixels = np.array(regionPixels['regionPixels'])
totPixels = len(regionPixels)
readme = add_update(update='%s pixels to consider.'%totPixels, readme=readme, verbose=verbose)

#----------------------------------------------------------------------------------------------
readme = add_update(update='\nSetting up the slicer ... ', readme=readme, verbose=verbose)
hpSlicer = slicers.HealpixSlicer(nside=nside, latLonDeg=opsdb.raDecInDeg, lonCol=pointingRACol, latCol=pointingDecCol)
hpSlicer.setupSlicer(simdata)    # slice data: know which pixels are observed in which visit

#----------------------------------------------------------------------------------------------
readme = add_update(update='\nSetting up the camera ... ', readme=readme, verbose=verbose)
camera = LsstSimMapper().camera
chipNames, obsIDs, fIDs, pixNums= [], [], [], []

#----------------------------------------------------------------------------------------------
readme = add_update(update='\nStarting the chip count ... ', readme=readme, verbose=verbose)
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
    if (delPercent>5):
        readme = add_update(update='%f%% pixels done\nTime passed (min): %f\n'%(percentDone, (time.time()-startTime)/60.),
                            readme=readme, verbose=verbose)
        prevPercent = percentDone
    #if (percentDone>1.):
    #    break
readme = add_update(update='\nAll done.\nTime passed (min): %f\n'%((time.time()-startTime)/60.),
                    readme=readme, verbose=verbose)

#----------------------------------------------------------------------------------------------
obsIDs, fIDs, chipNames, pixNums = np.array(obsIDs), np.array(fIDs), np.array(chipNames), np.array(pixNums)
readme = add_update(update='Unique obsHistIDs: %d \n## Unique chipNames: %d \n'%(len(np.unique(obsIDs)), len(np.unique(chipNames))),
                    readme=readme, verbose=verbose)

#  get rid of repeated entries; consolidate the data from unique observations.
readme = add_update(update='Consolidating the data ... ', readme=readme, verbose=verbose)
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
    
readme = add_update(update='Min, Max number of chips added by any given visit: %d, %s'%( min(numChips), max(numChips)),
          readme=readme, verbose=verbose)
readme = add_update(update='Total number of chips (across all visits to be simulated): %d'%sum(numChips),
          readme=readme, verbose=verbose)

#----------------------------------------------------------------------------------------------
out = pd.read_csv(visits_path)
if np.array(out['obsHistID'])!=obsIDsList:
    readme = add_update(update='\n##ObsIDs do not match.', readme=readme, verbose=verbose)
    if verbose:
        plt.clf()
        plt.hist(out['obsHistID'], label='saved before', histtype='step')
        plt.hist(obsIDsList, label='calculated here', histtype='step')
        plt.xlabel('Bins of obsIDs')
        plt.ylabel('Counts')
        plt.legend()
        plt.show()
else:
    readme = add_update(update='\n##ObsIDs do match.', readme=readme, verbose=verbose)
#----------------------------------------------------------------------------------------------
# save the data + readme
dataToSave = {'obsHistID': obsIDsList, 'fIDs': fIDsList, 'chipNames': chipNamesList}
filename = 'chipPerVisitData_%s_nside%s_%dNonWaveFrontChipsToSimulate.pickle'%(surveyRegionTag, nside, sum(numChips))
with open('%s/%s'%(output_path, filename), 'wb') as handle:
    pickle.dump(dataToSave, handle, protocol=pickle.HIGHEST_PROTOCOL)

readme = add_update(update='\nSaved %s in %s\n'%(filename, output_path), readme=readme, verbose=verbose)

readme += '\nTotal time taken: %.2f (min)\n\n'%((time.time()-startTime_0)/60.)

readme_file= open('%s/chipcount_readme_%s_nside%s_%schips.txt'%(output_path, surveyRegionTag, nside, sum(numChips)), 'a')
readme_file.write(readme)
readme_file.close()