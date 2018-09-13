This folder contains lists produced by various notebooks; please see the commit history for exact details.

For comprehensiveness, here's a quick summary:

#### All-Bands Visit Lists
The all-band csv files contain three columns: `band`, `obsHistID` and `fID`, where `band` is one of the six LSST filters, `obsHistID` is a "unique visit identifier" (as described [here](https://confluence.lsstcorp.org/display/SIM/Summary+Table+Column+Descriptions )) and `fID` is the fieldID (also described in the description linked before).
- `DC2VisitList_minion1016_v3_WFDvisits_nside1024_WFDvisitsInWFD.csv` and `DC2VisitList_minion1016_v3_DDvisits_nside1024_DDvisitsInuDD.csv` are produced by `DC2_Run2_visitList.ipynb`. The former includes *all* the WFD visits in the DC2 (WFD) footprint while the latter includes *all* the DD visits in the uDDF footprint.
- `DC2VisitList_minion1016_v3_WFDvisits_nside1024_WFDvisitsInWFD_subsetOverlapDDF.csv` is produced by `DC2_Run2_visitList_WFDoverlapDD.ipynb` and contains a subset of `DC2VisitList_minion1016_v3_WFDvisits_nside1024_WFDvisitsInWFD.csv`: only the WFD visits that overlap with the uDDF footprint. (Addresses [#7](https://github.com/LSSTDESC/DC2_visitList/issues/7 ))

#### Per-Band Visit Lists (Address [#4](https://github.com/LSSTDESC/DC2_visitList/issues/4 ))
The `per_band_lists` folder contains the visit lists for WFD (in WFD footprint) and DD (in uDDF footprint), now grouped by the filter band. They are produced by `create_per-band_lists.ipynb` and are a regrouping of the respective all-band visit lists. Each file only contains two columns: `obsHistID` and `expMJD`.

Similarly, the `per_band_lists_WFD_subset_overlap_DDF` folder contains the per-band visit lists for WFD visits that overlap with the uDDF footprint. They are produced by `create_per-band_lists_WFDvisit_overlapDD.ipynb`. (Addresses [#7](https://github.com/LSSTDESC/DC2_visitList/issues/7 ))

#### Per-Band, Per-Year Visit Lists (Address [#8](https://github.com/LSSTDESC/DC2_visitList/issues/8 ))
The `per_band_per_year_DD_lists` contains the visits lists for DD (in uDDF footprint), now grouped by the filter band AND year. They are produced by `create_per-band_per_year_lists_DD.ipynb` and are a regrouping of the all-band DD visit list. Each file only contains two columns: `obsHistID` and `expMJD`.

#### Per-Band, Filtered WFD Lists (from PR [#9](https://github.com/LSSTDESC/DC2_visitList/pull/9 ))
The `per_band_lists_WFD_filtered` contains visits lists of three types, for each band: WFD visits that pass the sky brightness limit and do not overlap with the DDF footprint (`DC2_Run2_<band>-band_WFDvisits_noDDF_noBright.txt`), and WFD visits that pass the sky brightness limit and overlap with the DDF footprint (`DC2_Run2_<band>-band_WFDvisits_DDF_notBright.txt`) and the WFD visits that do not pass the sky brightness limit (`DC2_Run2_<band>-band_WFDvisits_tooBright.txt`). These are produced by `visit_filter.py` and are a regrouping of the per-band WFD visit lists. Each file only contains two columns: `obsHistID` and `expMJD`.
