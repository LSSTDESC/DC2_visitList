#!/bin/bash

# source sims_maf
source /global/common/software/lsst/cori-haswell-gcc/stack/setup_current_sims.sh
# set up my own version rn
setup sims_maf -r /global/homes/a/awan/LSST/lsstRepos/sims_maf

# run the code for Run1 visits
# WFD
python /global/homes/a/awan/LSST/lsstRepos/DC2_visitList/DC2visitGen/code/count_chips.py -q --nside=512 \
                                                                                         --dataFolder='protoDC2Visits_nside512' \
                                                                                         --surveyRegionTag='WFD' &
# DD
python /global/homes/a/awan/LSST/lsstRepos/DC2_visitList/DC2visitGen/code/count_chips.py -q --nside=512 \
                                                                                         --dataFolder='protoDC2Visits_nside512' \
                                                                                         --surveyRegionTag='DD' &
# run the code for Run2 visits
# WFD
python /global/homes/a/awan/LSST/lsstRepos/DC2_visitList/DC2visitGen/code/count_chips.py -q --nside=1024 \
                                                                                         --dataFolder='DC2_Run2_Visits_nside1024' \
                                                                                         --surveyRegionTag='WFD' &
# DD
python /global/homes/a/awan/LSST/lsstRepos/DC2_visitList/DC2visitGen/code/count_chips.py -q --nside=1024 \
                                                                                         --dataFolder='DC2_Run2_Visits_nside1024' \
                                                                                         --surveyRegionTag='DD' &