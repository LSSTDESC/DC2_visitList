### DC2_visitList
This repo contains the code to create the visit list to simulate in DC2 as well as the outputs. The code was first developed within the [DC2_repo](https://github.com/humnaawan/DC2_Repo). Since only the final is necessary for the DC2 run itself, its better to have the code, and intermediate outputs outside the main repo. The relevant files were moved here from the fork while preserving history; following the steps listed [here](https://gist.github.com/humnaawan/3b24aa0632213acf1be03c12414b5b36).

The `DC2_visitList` notebooks run the code needed to produce the visit lists for Run 1-2; the specific Run number is in the respective notebook title. These notebooks save the visit lists across all six bands (available in this repo) as well as some GIF animations showing subsets of visits. The GIFs can be found on NERSC at `/global/cscratch1/sd/awan/DC2_gifs`

For Run 1, the WFD/DDF region coordinates were dictated by the protoDC2 extragalactic catalog. For Run 2, the WFD coordinates were found to maintain the relative position of the uDDF while expanding the WFD area to be close to 300deg2; see `DC2_Run2_regionCoords_WFD.ipynb` for details.

#### Misc notes:
- Run2 visits are found using HEALPix resolution paramater Nside= 1024, while Run1 visits were found with Nside= 512. Former is more reliable for estimating the footprint area, which is more critical for Run2.
- Run2 output folder contains visits for the uDDF but these are the same as that for Run1. The code was just for the uDDF to ensure consistency.
