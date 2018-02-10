/* 
sql script to add new dithered columns in a csv to the Summary table.

INPUTS:
    minion_1016_desc_v1.db  : OpSim database
    minion_1016_desc_dithered_noheaders_v2.csv : a csv files with all the columns and rows including the new dithered columns. Please note that the order must match the creation command beloe. There should be no headers in this file. 
*/
.open minion_1016_desc_v1.db
DROP TABLE Summary;
CREATE TABLE Summary (obsHistID INTEGER, sessionID INTEGER, propID INTEGER, fieldID INTEGER, fieldRA REAL, fieldDec REAL, filter TEXT, expDate INTEGER, expMJD REAL, night INTEGER, visitTime REAL, visitExpTime REAL, finRank REAL, FWHMeff REAL, FWHMgeom REAL, transparency REAL, airmass REAL, vSkyBright REAL, filtSkyBrightness REAL, rotSkyPos REAL, rotTelPos REAL, lst REAL, altitude REAL, azimuth REAL, dist2Moon REAL, solarElong REAL, moonRA REAL, moonDec REAL, moonAlt REAL, moonAZ REAL, moonPhase REAL, sunAlt REAL, sunAz REAL, phaseAngle REAL, rScatter REAL, mieScatter REAL, moonIllum REAL, moonBright REAL, darkBright REAL, rawSeeing REAL, wind REAL, humidity REAL, slewDist REAL, slewTime REAL, fiveSigmaDepth REAL, ditheredRA REAL, ditheredDec REAL, descDitheredDec REAL, descDitheredRA REAL, descDitheredRotTelPos REAL);
.mode csv
.import minion_1016_desc_dithered_noheader_v2.csv Summary
CREATE INDEX fieldID_idx ON Summary(fieldID);
CREATE INDEX expMJD_idx ON Summary(expMJD);
CREATE INDEX filter_idx ON Summary(filter);
CREATE INDEX fieldRA_idx ON Summary(fieldRA);
CREATE INDEX fieldDec_idx ON Summary(fieldDec);
CREATE INDEX fieldRADec_idx ON Summary(fieldRA, fieldDec);
CREATE INDEX night_idx ON Summary(night);
CREATE INDEX propID_idx ON Summary(propID);
CREATE INDEX ditheredRA_idx ON Summary(ditheredRA);
CREATE INDEX ditheredDec_idx ON Summary(ditheredDec);
CREATE INDEX ditheredRADec_idx ON Summary(ditheredRA, ditheredDec);
CREATE INDEX filter_propID_idx ON Summary(filter, propID);
