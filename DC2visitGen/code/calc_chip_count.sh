#!/bin/bash

# source sims_maf
source /global/common/software/lsst/cori-haswell-gcc/stack/setup_current_sims.sh
# set up my own version rn
setup sims_maf -r /global/homes/a/awan/LSST/lsstRepos/sims_maf

# run the code for Run1 visits
python count_chips.py --nside=512 --dataFolder='protoDC2Visits_nside512' -q --surveyRegionTag='WFD' &
python count_chips.py --nside=512 --dataFolder='protoDC2Visits_nside512' -q --surveyRegionTag='DD' &

# run the code for Run2 visits
python count_chips.py --nside=1024 --dataFolder='DC2_Run2_Visits_nside1024' -q --surveyRegionTag='WFD' &
python count_chips.py --nside=1024 --dataFolder='DC2_Run2_Visits_nside1024' -q --surveyRegionTag='DD' &