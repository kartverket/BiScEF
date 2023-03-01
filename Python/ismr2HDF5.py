# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 13:35:13 2023

@author: saschu
"""



import h5py
import sys
sys.path.append('C:\\Users\\saschu\\OneDrive - Danmarks Tekniske Universitet\\phd\\Code\\Python\\') #path to ISMR package
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning) #supresses FutureWarnings
from ISMR import loadISMR
from ISMR import constellations
from ISMR import timeISMR

yr = "21" # year
#doy = list(range(60,91))
doy = [308]
station = ["SCO3"] # list of stations
elmask = 0 # cutoff angle for elevation mask
contype = ['G','E','C','R','SBAS','QZSS','IRNSS'] #GNSS constellations G: GPS, R: GLONASS, E: Galileo, C: Beidou


ismrfile = loadISMR.load(doy,yr,station,elmask,contype)
# Create a HDF5 file

fileOpenMode    = "w";
hdfFileName     = f"{station[0]}{doy[0]}{yr}.h5";
hdf5File        = h5py.File(hdfFileName, fileOpenMode);
 


Data  = hdf5File.create_group("/ismr");

Data.attrs["Receiver"] = "PolaRx5S"
Data.attrs["Station"] = f"{station[0]}"
Data.attrs["StationLatLon"] = "70.49,-21.95"
Data.attrs["CutoffFrequency"] = "0.1 Hz"
Data.attrs["Filter"] = "6th order Butterworth"
Data.attrs["Constellations"] = f"{contype}"

datasetShape = (len(ismrfile),);

GPSweek = Data.create_dataset("/ismr/GPSweek", datasetShape)
TOW = Data.create_dataset("/ismr/TOW", datasetShape);
SVID = Data.create_dataset("/ismr/SVID", datasetShape)
Rxstate = Data.create_dataset("/ismr/Rxstate", datasetShape)
Azimuth = Data.create_dataset("/ismr/Azimuth", datasetShape)
Elevation = Data.create_dataset("/ismr/Elevation", datasetShape)
AvgCN0s1 = Data.create_dataset("/ismr/AvgCN0s1", datasetShape)
S4s1 = Data.create_dataset("/ismr/S4s1", datasetShape)
S4cors1 = Data.create_dataset("/ismr/S4cors1", datasetShape)
Phi01s1 = Data.create_dataset("/ismr/Phi01s1", datasetShape)
Phi03s1 = Data.create_dataset("/ismr/Phi03s1", datasetShape)
Phi10s1 = Data.create_dataset("/ismr/Phi10s1", datasetShape)
Phi30s1 = Data.create_dataset("/ismr/Phi30s1", datasetShape)
Phi60s1 = Data.create_dataset("/ismr/Phi60s1", datasetShape)
AvgCCDs1 = Data.create_dataset("/ismr/AvgCCDs1", datasetShape)
SigmaCCDs1 = Data.create_dataset("/ismr/SigmaCCDs1", datasetShape)
TEC45 = Data.create_dataset("/ismr/TEC45", datasetShape)
dTEC6045 = Data.create_dataset("/ismr/dTEC6045", datasetShape)
TEC30 = Data.create_dataset("/ismr/TEC30", datasetShape)
dTEC4530 = Data.create_dataset("/ismr/dTEC4530", datasetShape)
TEC15 = Data.create_dataset("/ismr/TEC15", datasetShape)
dTEC3015 = Data.create_dataset("/ismr/dTEC3015", datasetShape)
TECtow = Data.create_dataset("/ismr/TECtow", datasetShape)
dTEC15tow = Data.create_dataset("/ismr/dTEC15tow", datasetShape)
lockts1 = Data.create_dataset("/ismr/lockts1", datasetShape)
SBFver = Data.create_dataset("/ismr/SBFver", datasetShape)
locktTEC = Data.create_dataset("/ismr/locktTEC", datasetShape)
CN0TEC = Data.create_dataset("/ismr/CN0TEC", datasetShape)
SIs1 = Data.create_dataset("/ismr/SIs1", datasetShape)
SInums1 = Data.create_dataset("/ismr/SInums1", datasetShape)
ps1 = Data.create_dataset("/ismr/ps1", datasetShape)
AvgCN0s2 = Data.create_dataset("/ismr/AvgCN0s2", datasetShape)
S4s2 = Data.create_dataset("/ismr/S4s2", datasetShape)
S4cors2 = Data.create_dataset("/ismr/S4cors2", datasetShape)
Phi01s2 = Data.create_dataset("/ismr/Phi01s2", datasetShape)
Phi03s2 = Data.create_dataset("/ismr/Phi03s2", datasetShape)
Phi10s2 = Data.create_dataset("/ismr/Phi10s2", datasetShape)
Phi30s2 = Data.create_dataset("/ismr/Phi30s2", datasetShape)
Phi60s2 = Data.create_dataset("/ismr/Phi60s2", datasetShape)
AvgCCDs2 = Data.create_dataset("/ismr/AvgCCDs2", datasetShape)
SigmaCCDs2 = Data.create_dataset("/ismr/SigmaCCDs2", datasetShape)
lockts2 = Data.create_dataset("/ismr/lockts2", datasetShape)
SIs2 = Data.create_dataset("/ismr/SIs2", datasetShape)
SInums2 = Data.create_dataset("/ismr/SInums2", datasetShape)
ps2 = Data.create_dataset("/ismr/ps2", datasetShape)
AvgCN0s3 = Data.create_dataset("/ismr/AvgCN0s3", datasetShape)
S4s3 = Data.create_dataset("/ismr/S4s3", datasetShape)
S4cors3 = Data.create_dataset("/ismr/S4cors3", datasetShape)
Phi01s3 = Data.create_dataset("/ismr/Phi01s3", datasetShape)
Phi03s3 = Data.create_dataset("/ismr/Phi03s3", datasetShape)
Phi10s3 = Data.create_dataset("/ismr/Phi10s3", datasetShape)
Phi30s3 = Data.create_dataset("/ismr/Phi30s3", datasetShape)
Phi60s3 = Data.create_dataset("/ismr/Phi60s3", datasetShape)
AvgCCDs3 = Data.create_dataset("/ismr/AvgCCDs3", datasetShape)
SigmaCCDs3 = Data.create_dataset("/ismr/SigmaCCDs3", datasetShape)
lockts3 = Data.create_dataset("/ismr/lockts3", datasetShape)
SIs3 = Data.create_dataset("/ismr/SIs3", datasetShape)
SInums3 = Data.create_dataset("/ismr/SInums3", datasetShape)
ps3 = Data.create_dataset("/ismr/ps3", datasetShape)
Ts1 = Data.create_dataset("/ismr/Ts1", datasetShape)
Ts2 = Data.create_dataset("/ismr/Ts2", datasetShape)
Ts3 = Data.create_dataset("/ismr/Ts3", datasetShape)

# Add

GPSweek.attrs["Description"] = "GPS week number since 06 January 1980. The weeks run from Sunday to Saturday.";
TOW.attrs["Description"] = "The second of the week starting from Sunday";
SVID.attrs["Description"] = "Satellite vechile ID";
Rxstate.attrs["Description"] = "Value of the RxState field of the ReceiverStatus SBF block"
Azimuth.attrs["Description"] = "Azimuth of satellite [degrees]" 
Elevation.attrs["Description"] = "Elevation of satellite [degrees]"
AvgCN0s1.attrs["Description"] = "Average signal 1 C/N0 over the last minute [dB-Hz]"
S4s1.attrs["Description"] = "Total S4 on signal 1"
S4cors1.attrs["Description"] = "Correction to total S4 on signal 1"
Phi01s1.attrs["Description"] = "1-second phase sigma on signal 1 [radians]"
Phi03s1.attrs["Description"] = "3-second phase sigma on signal 1 [radians]"
Phi10s1.attrs["Description"] = "10-second phase sigma on signal 1 [radians]"
Phi30s1.attrs["Description"] = "30-second phase sigma on signal 1 [radians]"
Phi60s1.attrs["Description"] = "60-second phase sigma on signal 1 [radians]"
AvgCCDs1.attrs["Description"] = "Average code-carrier divergence for signal 1 [meters]"
SigmaCCDs1.attrs["Description"] = "Standard deviation of code-carrier divergence for signal 1 [meters]"
TEC45.attrs["Description"] = "TEC at TOW-45 sec, with calibration [TECU]"
dTEC6045.attrs["Description"] = "dTEC from TOW-60 to TOW-45 [TECU]"
TEC30.attrs["Description"] = "TEC at TOW-30 sec, with calibration [TECU]"
dTEC4530.attrs["Description"] = "dTEC from TOW-45 to TOW-30 [TECU]"
TEC15.attrs["Description"] = "TEC at TOW-15 sec, with calibration [TECU]"
dTEC3015.attrs["Description"] = "dTEC from TOW-30 to TOW-15 [TECU]"
TECtow.attrs["Description"] = "TEC at TOW, with calibration [TECU]"
dTEC15tow.attrs["Description"] = "dTEC from TOW-15 to TOW [TECU]"
lockts1.attrs["Description"] = "Signal lock time for signal 1 [seconds]"
SBFver.attrs["Description"] = "SBF version number"
locktTEC.attrs["Description"] = "Lock time on second frequency used for TEC computation [seconds]"
CN0TEC.attrs["Description"] = "Average C/N0 of seconde frequency used for TEC computation [dB-Hz]"
SIs1.attrs["Description"] = "SI index on signal 1"
SInums1.attrs["Description"] = "Numerator of SI index on signal 1"
ps1.attrs["Description"] = "Spectral slope for detrended phase in the 0.1 to 25 Hz range for signal 1 "
AvgCN0s2.attrs["Description"] = "Average signal 2 C/N0 over the last minute [dB-Hz]"
S4s2.attrs["Description"] = "Total S4 on signal 2"
S4cors2.attrs["Description"] = "Correction to total S4 on signal 2"
Phi01s2.attrs["Description"] = "1-second phase sigma on signal 2 [radians]"
Phi03s2.attrs["Description"] = "3-second phase sigma on signal 2 [radians]"
Phi10s2.attrs["Description"] = "10-second phase sigma on signal 2 [radians]"
Phi30s2.attrs["Description"] = "30-second phase sigma on signal 2 [radians]"
Phi60s2.attrs["Description"] = "60-second phase sigma on signal 2 [radians]"
AvgCCDs2.attrs["Description"] = "Average code-carrier divergence for signal 2 [meters]"
SigmaCCDs2.attrs["Description"] = "Standard deviation of code-carrier divergence for signal 2 [meters]"
lockts2.attrs["Description"] = "Signal lock time for signal 2 [seconds]"
SIs2.attrs["Description"] = "SI index on signal 2"
SInums2.attrs["Description"] = "Numerator of SI index on signal 2"
ps2.attrs["Description"] = "Spectral slope for detrended phase in the 0.1 to 25 Hz range for signal 2"
AvgCN0s3.attrs["Description"] = "Average signal 3 C/N0 over the last minute [dB-Hz]"
S4s3.attrs["Description"] = "Total S4 on signal 3"
S4cors3.attrs["Description"] = "Correction to total S4 on signal 3"
Phi01s3.attrs["Description"] = "1-second phase sigma on signal 3 [radians]"
Phi03s3.attrs["Description"] = "3-second phase sigma on signal 3 [radians]"
Phi10s3.attrs["Description"] = "10-second phase sigma on signal 3 [radians]"
Phi30s3.attrs["Description"] = "30-second phase sigma on signal 3 [radians]"
Phi60s3.attrs["Description"] = "60-second phase sigma on signal 3 [radians]"
AvgCCDs3.attrs["Description"] = "Average code-carrier divergence for signal 3 [meters]"
SigmaCCDs3.attrs["Description"] = "Standard deviation of code-carrier divergence for signal 3 [meters]"
lockts3.attrs["Description"] = "Signal lock time for signal 3 [seconds]"
SIs3.attrs["Description"] = "SI index on signal 3"
SInums3.attrs["Description"] = "Numerator of SI index on signal 2"
ps3.attrs["Description"] = "Spectral slope for detrended phase in the 0.1 to 25 Hz range for signal 3"
Ts1.attrs["Description"] = "Phase power spectral density at 1 Hz on signal 1 [rad^2/Hz]"
Ts2.attrs["Description"] = "Phase power spectral density at 1 Hz on signal 2 [rad^2/Hz]"
Ts3.attrs["Description"] = "Phase power spectral density at 1 Hz on signal 3 [rad^2/Hz]"

# Assign hourly readings

for i in range(0, len(ismrfile)):

    GPSweek[i] = ismrfile['GPSweek'][i]
    TOW[i] = ismrfile['TOW'][i]
    SVID[i] = ismrfile['sv'][i]
    Rxstate[i] = ismrfile['Rxstate'][i]
    Azimuth[i] = ismrfile['Azimuth'][i]
    Elevation[i] = ismrfile['Elevation'][i]
    AvgCN0s1[i] = ismrfile['AvgCN0s1'][i]
    S4s1[i] = ismrfile['S4s1'][i]
    S4cors1[i] = ismrfile['S4cors1'][i]
    Phi01s1[i] = ismrfile['Phi01s1'][i]
    Phi03s1[i] = ismrfile['Phi03s1'][i]
    Phi10s1[i] = ismrfile['Phi10s1'][i]
    Phi30s1[i] = ismrfile['Phi30s1'][i]
    Phi60s1[i] = ismrfile['Phi60s1'][i]
    AvgCCDs1[i] = ismrfile['AvgCCDs1'][i]
    SigmaCCDs1[i] = ismrfile['SigmaCCDs1'][i]
    TEC45[i] = ismrfile['TEC45'][i]
    dTEC6045[i] = ismrfile['dTEC6045'][i]
    TEC30[i] = ismrfile['TEC30'][i]
    dTEC4530[i] = ismrfile['dTEC4530'][i]
    TEC15[i] = ismrfile['TEC15'][i]
    dTEC3015[i] = ismrfile['dTEC3015'][i]
    TECtow[i] = ismrfile['TECtow'][i]
    dTEC15tow[i] = ismrfile['dTEC15tow'][i]
    lockts1[i] = ismrfile['lockts1'][i]
    SBFver[i] = ismrfile['sbfver'][i]
    locktTEC[i] = ismrfile['Phi01s1'][i]
    CN0TEC[i] = ismrfile['CN0TEC'][i]
    SIs1[i] = ismrfile['SIs1'][i]
    SInums1[i] = ismrfile['SInums1'][i]
    ps1[i] = ismrfile['ps1'][i]
    AvgCN0s2[i] = ismrfile['AvgCN0s2'][i]
    S4s2[i] = ismrfile['S4s2'][i]
    S4cors2[i] = ismrfile['S4cors2'][i]
    Phi01s2[i] = ismrfile['Phi01s2'][i]
    Phi03s2[i] = ismrfile['Phi03s2'][i]
    Phi10s2[i] = ismrfile['Phi10s2'][i]
    Phi30s2[i] = ismrfile['Phi30s2'][i]
    Phi60s2[i] = ismrfile['Phi60s2'][i]
    AvgCCDs2[i] = ismrfile['AvgCCDs2'][i]
    SigmaCCDs2[i] = ismrfile['SigmaCCDs2'][i]
    lockts2[i] = ismrfile['lockts2'][i]
    SIs2[i] = ismrfile['SIs2'][i]
    SInums2[i] = ismrfile['SInums2'][i]
    ps2[i] = ismrfile['ps2'][i]
    AvgCN0s3[i] = ismrfile['AvgCN0s3'][i]
    S4s3[i] = ismrfile['S4s3'][i]
    S4cors3[i] = ismrfile['S4cors3'][i]
    Phi01s3[i] = ismrfile['Phi01s3'][i]
    Phi03s3[i] = ismrfile['Phi03s3'][i]
    Phi10s3[i] = ismrfile['Phi10s3'][i]
    Phi30s3[i] = ismrfile['Phi30s3'][i]
    Phi60s3[i] = ismrfile['Phi60s3'][i]
    AvgCCDs3[i] = ismrfile['AvgCCDs3'][i]
    SigmaCCDs3[i] = ismrfile['SigmaCCDs3'][i]
    lockts3[i] = ismrfile['lockts3'][i]
    SIs3[i] = ismrfile['SIs3'][i]
    SInums3[i] = ismrfile['SInums3'][i]
    ps3[i] = ismrfile['ps3'][i]
    Ts1 = ismrfile['Ts1'][i]
    Ts2 = ismrfile['Ts2'][i]
    Ts3 = ismrfile['Ts3'][i]


hdf5File.close()
