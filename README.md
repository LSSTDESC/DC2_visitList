### DC2_visitList
This repo contains the code to create the visit list to simulate in DC2 as well as the outputs. The code was first developed within the [DC2_repo](https://github.com/humnaawan/DC2_Repo). Since only the final is necessary for the DC2 run itself, its better to have the code, and intermediate outputs outside the main repo. The relevant files were moved here from the fork while preserving history; following the steps listed [here](https://gist.github.com/humnaawan/3b24aa0632213acf1be03c12414b5b36).

#### Code Details
The `DC2_Run<>_visitList.ipynb` notebooks run [getDC2VisitList](https://github.com/LSSTDESC/DC2_visitList/blob/a0a499d500d174c358e95594bfc897416f31cd54/DC2visitGen/code/DC2_visitListCode.py#L91 ) to produce the visit lists for Run 1-2; the specific Run number is in the respective notebook title. These notebooks save the visit lists across all six bands (available in this repo) as well as some GIF animations showing subsets of visits (produced by [DC2VisitsSim](https://github.com/LSSTDESC/DC2_visitList/blob/a0a499d500d174c358e95594bfc897416f31cd54/DC2visitGen/code/DC2_visitsSim.py#L18 )). The GIFs are on NERSC at `/global/homes/a/awan/desc/DC2_gifs` and should be readable by anyone with `lsst` group affiliation.

Finally, `create_per-band_lists.ipynb` creates the per-band lists for Run 2 (after checking that the analog lists for Run 1.1 match those that were produced by [this](https://github.com/LSSTDESC/DC2-production/blob/master/Notebooks/survey_design_visit_lists.ipynb) notebook). The code basically takes the all-band lists, appends expMJD column, groups the visits by band, and then saves obsHistID and expMJD columns for each band.

#### Region Coordinates
- For Run 1, the WFD/DDF region coordinates were dictated by the protoDC2 extragalactic catalog.
- For Run 2, the WFD coordinates were found to maintain the relative position of the uDDF while expanding the WFD area to be close to 300deg2; see `DC2_Run2_regionCoords_WFD.ipynb` for details.

#### Misc notes:
- Run 2 visits are found using HEALPix resolution paramater Nside 1024, while Run1 visits were found with Nside 512. Former is more reliable for estimating the footprint area, which is more critical for Run 2.
- Run 2 output folder contains visits for the uDDF but these are the same as that for Run 1. The code was just used for the uDDF to ensure consistency;  `DC2_Run2_visitList.ipynb` notebook checks this in its last output cell.