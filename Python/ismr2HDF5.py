# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 13:35:13 2023

@author: saschu
"""

import h5py
import sys
import datetime
import pandas as pd
sys.path.append('C:\\Users\\saschu\\OneDrive - Danmarks Tekniske Universitet\\phd\\Code\\Python\\') #path to ISMR package
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning) #supresses FutureWarnings
from ISMR import loadISMR
from ISMR import constellations
from ISMR import timeISMR
from ISMR import ismrIPP

yr = "23" # year
#doy = list(range(60,91))
doy = [62]
station = ["KLQ2"] # list of stations
country = "GRL"
elmask = 0 # cutoff angle for elevation mask
contype = ['G','E','C','R','S','J','I'] #GNSS constellations G: GPS, R: GLONASS, E: Galileo, C: Beidou
Hipp = 300 # in km
ismrfile = loadISMR.load(doy,yr,station,elmask,contype)

# Create a HDF5 file
date = datetime.datetime(2000+int(yr), 1, 1) + datetime.timedelta(doy[0] - 1)
month = '{:02d}'.format(date.month)
day = '{:02d}'.format(date.day)

fileOpenMode    = "w";
hdfFileName     = f"{country}{station[0]}{2000+int(yr)}{month}{day}.nc";
hdf5File        = h5py.File(hdfFileName, fileOpenMode);
 
## Attributes at root level
hdf5File.attrs["BiScEFVersion"] = "0.1"
hdf5File.attrs["ReceiverType"] = "PolaRx5S"
hdf5File.attrs["ReceiverCode"] = f"{station[0]}"
hdf5File.attrs["ReceiverLongitude"] = -50.6202
hdf5File.attrs["ReceiverLatitude"] = 66.9956
hdf5File.attrs["ReceiverSamplingRate"] = float(100)
hdf5File.attrs["AntennaType"] = "LEIAR25.R4" #For THU5 and UPV1 it is LEIAR20

hdf5File.attrs["Constellations"] = ' '.join(contype)
hdf5File.attrs["SignalStatement"] = "Sig1 means L1CA for GPS/GLONASS/SBAS/QZSS, L1BC for Galileo, and B1 for COMPASS. Sig2 means L2C for GPS/GLONASS/QZSS, E5a for Galileo, L5 for SBAS, and B2 for COMPASS. Sig3 means L5 for GPS/QZSS or E5b for Galileo"
hdf5File.attrs["PhaseHighPassFilterFreqCutoff"] = 0.1
hdf5File.attrs["PhaseHighPassFilterType"] = "6th order Butterworth"
hdf5File.attrs["ElevationCutoff"] = float(elmask)
hdf5File.attrs["SLMHeight"] = float(Hipp)*1000 # in meters

datasetShape = (len(ismrfile),);

#Compute unix time
gpsTime = pd.Series([])
gpsEpoch = datetime.datetime(1980,1,6,0,0,0)
unixEpoch = datetime.datetime(1970,1,1,0,0,0)
gpsDT = ismrfile.TOW+ismrfile.GPSweek*604800
gpsTime = [gpsEpoch + datetime.timedelta(seconds=x) for x in gpsDT]
unixTime = [(x - unixEpoch).total_seconds() for x in gpsTime]

#Computer IPP lat and lon
[lonIPP,latIPP] = ismrIPP.IPP(ismrfile,station[0],Hipp)

#Create datasets
GPSweek = hdf5File.create_dataset("GPSweek", datasetShape)
TOW = hdf5File.create_dataset("TOW", datasetShape)
UNIXTime = hdf5File.create_dataset("UNIXTime", datasetShape) 
SVID = hdf5File.create_dataset("SVID", datasetShape)
Azimuth = hdf5File.create_dataset("Azimuth", datasetShape)
Elevation = hdf5File.create_dataset("Elevation", datasetShape)
Longitude = hdf5File.create_dataset("Longitude", datasetShape)
Latitude = hdf5File.create_dataset("Latitude", datasetShape)
Sept_Rxstate = hdf5File.create_dataset("Sept_Rxstate", datasetShape)
Sept_sbf2ismrversion = hdf5File.create_dataset("Sept_sbf2ismrversion", datasetShape)

AvgCN0s1 = hdf5File.create_dataset("AvgCN0s1", datasetShape)
S4s1 = hdf5File.create_dataset("S4s1", datasetShape)
S4cors1 = hdf5File.create_dataset("S4cors1", datasetShape)
Phi01s1 = hdf5File.create_dataset("Phi01s1", datasetShape)
Phi03s1 = hdf5File.create_dataset("Phi03s1", datasetShape)
Phi10s1 = hdf5File.create_dataset("Phi10s1", datasetShape)
Phi30s1 = hdf5File.create_dataset("Phi30s1", datasetShape)
Phi60s1 = hdf5File.create_dataset("Phi60s1", datasetShape)
AvgCCDs1 = hdf5File.create_dataset("AvgCCDs1", datasetShape)
SigmaCCDs1 = hdf5File.create_dataset("SigmaCCDs1", datasetShape)
lockts1 = hdf5File.create_dataset("lockts1", datasetShape)
SIs1 = hdf5File.create_dataset("SIs1", datasetShape)
SInums1 = hdf5File.create_dataset("SInums1", datasetShape)
ps1 = hdf5File.create_dataset("ps1", datasetShape)
Ts1 = hdf5File.create_dataset("Ts1", datasetShape)

AvgCN0s2 = hdf5File.create_dataset("AvgCN0s2", datasetShape)
S4s2 = hdf5File.create_dataset("S4s2", datasetShape)
S4cors2 = hdf5File.create_dataset("S4cors2", datasetShape)
Phi01s2 = hdf5File.create_dataset("Phi01s2", datasetShape)
Phi03s2 = hdf5File.create_dataset("Phi03s2", datasetShape)
Phi10s2 = hdf5File.create_dataset("Phi10s2", datasetShape)
Phi30s2 = hdf5File.create_dataset("Phi30s2", datasetShape)
Phi60s2 = hdf5File.create_dataset("Phi60s2", datasetShape)
AvgCCDs2 = hdf5File.create_dataset("AvgCCDs2", datasetShape)
SigmaCCDs2 = hdf5File.create_dataset("SigmaCCDs2", datasetShape)
lockts2 = hdf5File.create_dataset("lockts2", datasetShape)
SIs2 = hdf5File.create_dataset("SIs2", datasetShape)
SInums2 = hdf5File.create_dataset("SInums2", datasetShape)
ps2 = hdf5File.create_dataset("ps2", datasetShape)
Ts2 = hdf5File.create_dataset("Ts2", datasetShape)

AvgCN0s3 = hdf5File.create_dataset("AvgCN0s3", datasetShape)
S4s3 = hdf5File.create_dataset("S4s3", datasetShape)
S4cors3 = hdf5File.create_dataset("S4cors3", datasetShape)
Phi01s3 = hdf5File.create_dataset("Phi01s3", datasetShape)
Phi03s3 = hdf5File.create_dataset("Phi03s3", datasetShape)
Phi10s3 = hdf5File.create_dataset("Phi10s3", datasetShape)
Phi30s3 = hdf5File.create_dataset("Phi30s3", datasetShape)
Phi60s3 = hdf5File.create_dataset("Phi60s3", datasetShape)
AvgCCDs3 = hdf5File.create_dataset("AvgCCDs3", datasetShape)
SigmaCCDs3 = hdf5File.create_dataset("SigmaCCDs3", datasetShape)
lockts3 = hdf5File.create_dataset("lockts3", datasetShape)
SIs3 = hdf5File.create_dataset("SIs3", datasetShape)
SInums3 = hdf5File.create_dataset("SInums3", datasetShape)
ps3 = hdf5File.create_dataset("ps3", datasetShape)
Ts3 = hdf5File.create_dataset("Ts3", datasetShape)

TEC45 = hdf5File.create_dataset("TEC45", datasetShape)
dTEC6045 = hdf5File.create_dataset("dTEC6045", datasetShape)
TEC30 = hdf5File.create_dataset("TEC30", datasetShape)
dTEC4530 = hdf5File.create_dataset("dTEC4530", datasetShape)
TEC15 = hdf5File.create_dataset("TEC15", datasetShape)
dTEC3015 = hdf5File.create_dataset("dTEC3015", datasetShape)
TECtow = hdf5File.create_dataset("TECtow", datasetShape)
dTEC15tow = hdf5File.create_dataset("dTEC15tow", datasetShape)
locktTEC = hdf5File.create_dataset("locktTEC", datasetShape)

CN0TEC = hdf5File.create_dataset("CN0TEC", datasetShape)


# Attributes for datasets
GPSweek.attrs["Description"] = "GPS week number since 06 January 1980. The weeks run from Sunday to Saturday."
GPSweek.attrs["Unit"] = "Week"
TOW.attrs["Description"] = "The second of the week starting from Sunday"
TOW.attrs["Unit"] = "Seconds"
UNIXTime.attrs["Description"] = "Seconds since Jan 01 1970 UTC."
UNIXTime.attrs["Unit"] = "Seconds"
SVID.attrs["Description"] = "Satellite vechile ID"
Azimuth.attrs["Description"] = "Azimuth of satellite."
Azimuth.attrs["Unit"] = "Degrees"
Elevation.attrs["Description"] = "Elevation of satellite."
Elevation.attrs["Unit"] = "Degrees"
Longitude.attrs["Description"] = "Longitude of the Ionospheric Pierce Point (IPP)."
Longitude.attrs["Unit"] = "Degrees East"
Latitude.attrs["Description"] = "Latitude of the Ionospheric Pierce Point (IPP)."
Latitude.attrs["Unit"] = "Degrees North"
Sept_Rxstate.attrs["Description"] = "Value of the RxState field of the ReceiverStatus SBF block."
Sept_sbf2ismrversion.attrs["Description"] = "sbf2ismr version number."

AvgCN0s1.attrs["Description"] = "Average signal 1 C/N0 over the last minute."
AvgCN0s1.attrs["Unit"] = "dB-Hz"
S4s1.attrs["Description"] = "Total S4 on signal 1."
S4cors1.attrs["Description"] = "Correction to total S4 on signal 1."
Phi01s1.attrs["Description"] = "1-second phase sigma on signal 1."
Phi01s1.attrs["Unit"] = "Radians"
Phi03s1.attrs["Description"] = "3-second phase sigma on signal 1."
Phi03s1.attrs["Unit"] = "Radians"
Phi10s1.attrs["Description"] = "10-second phase sigma on signal 1."
Phi10s1.attrs["Unit"] = "Radians"
Phi30s1.attrs["Description"] = "30-second phase sigma on signal 1."
Phi30s1.attrs["Unit"] = "Radians"
Phi60s1.attrs["Description"] = "60-second phase sigma on signal 1."
Phi60s1.attrs["Unit"] = "Radians"
AvgCCDs1.attrs["Description"] = "Average code-carrier divergence for signal 1."
AvgCCDs1.attrs["Unit"] = "Meters"
SigmaCCDs1.attrs["Description"] = "Standard deviation of code-carrier divergence for signal 1."
SigmaCCDs1.attrs["Unit"] = "Meters"
lockts1.attrs["Description"] = "Signal lock time for signal 1."
lockts1.attrs["Unit"] = "Seconds"
SIs1.attrs["Description"] = "SI index on signal 1"
SInums1.attrs["Description"] = "Numerator of SI index on signal 1"
ps1.attrs["Description"] = "Spectral slope for detrended phase in the 0.1 to 25 Hz range for signal 1"
Ts1.attrs["Description"] = "Phase power spectral density at 1 Hz on signal 1."
Ts1.attrs["Unit"] = "Radians^2/Hz"

AvgCN0s2.attrs["Description"] = "Average signal 2 C/N0 over the last minute."
AvgCN0s2.attrs["Unit"] = "dB-Hz"
S4s2.attrs["Description"] = "Total S4 on signal 2."
S4cors2.attrs["Description"] = "Correction to total S4 on signal 2."
Phi01s2.attrs["Description"] = "1-second phase sigma on signal 2."
Phi01s2.attrs["Unit"] = "Radians"
Phi03s2.attrs["Description"] = "3-second phase sigma on signal 2."
Phi03s2.attrs["Unit"] = "Radians"
Phi10s2.attrs["Description"] = "10-second phase sigma on signal 2."
Phi10s2.attrs["Unit"] = "Radians"
Phi30s2.attrs["Description"] = "30-second phase sigma on signal 2."
Phi30s2.attrs["Unit"] = "Radians"
Phi60s2.attrs["Description"] = "60-second phase sigma on signal 2."
Phi60s2.attrs["Unit"] = "Radians"
AvgCCDs2.attrs["Description"] = "Average code-carrier divergence for signal 2."
AvgCCDs2.attrs["Unit"] = "Meters"
SigmaCCDs2.attrs["Description"] = "Standard deviation of code-carrier divergence for signal 2."
SigmaCCDs2.attrs["Unit"] = "Meters"
lockts2.attrs["Description"] = "Signal lock time for signal 2."
lockts2.attrs["Unit"] = "Seconds"
SIs2.attrs["Description"] = "SI index on signal 2."
SInums2.attrs["Description"] = "Numerator of SI index on signal 2."
ps2.attrs["Description"] = "Spectral slope for detrended phase in the 0.1 to 25 Hz range for signal 2."
Ts2.attrs["Description"] = "Phase power spectral density at 1 Hz on signal 2."
Ts2.attrs["Unit"] = "Radians^2/Hz"

AvgCN0s3.attrs["Description"] = "Average signal 3 C/N0 over the last minute."
AvgCN0s3.attrs["Unit"] = "dB-Hz"
S4s3.attrs["Description"] = "Total S4 on signal 3"
S4cors3.attrs["Description"] = "Correction to total S4 on signal 3"
Phi01s3.attrs["Description"] = "1-second phase sigma on signal 3."
Phi01s3.attrs["Unit"] = "Radians"
Phi03s3.attrs["Description"] = "3-second phase sigma on signal 3."
Phi03s3.attrs["Unit"] = "Radians"
Phi10s3.attrs["Description"] = "10-second phase sigma on signal 3."
Phi10s3.attrs["Unit"] = "Radians"
Phi30s3.attrs["Description"] = "30-second phase sigma on signal 3."
Phi30s3.attrs["Unit"] = "Radians"
Phi60s3.attrs["Description"] = "60-second phase sigma on signal 3."
Phi60s3.attrs["Unit"] = "Radians"
AvgCCDs3.attrs["Description"] = "Average code-carrier divergence for signal 3."
AvgCCDs3.attrs["Description"] = "Meters"
SigmaCCDs3.attrs["Description"] = "Standard deviation of code-carrier divergence for signal 3."
SigmaCCDs3.attrs["Unit"] = "Meters"
lockts3.attrs["Description"] = "Signal lock time for signal 3."
lockts3.attrs["Unit"] = "Seconds"
SIs3.attrs["Description"] = "SI index on signal 3"
SInums3.attrs["Description"] = "Numerator of SI index on signal 3"
ps3.attrs["Description"] = "Spectral slope for detrended phase in the 0.1 to 25 Hz range for signal 3"
Ts3.attrs["Description"] = "Phase power spectral density at 1 Hz on signal 3."
Ts3.attrs["Unit"] = "Radians^2/Hz"

TEC45.attrs["Description"] = "TEC at TOW-45 sec, with calibration."
TEC45.attrs["Unit"] = "TECU"
dTEC6045.attrs["Description"] = "dTEC from TOW-60 to TOW-45."
dTEC6045.attrs["Unit"] = "TECU"
TEC30.attrs["Description"] = "TEC at TOW-30 sec, with calibration."
TEC30.attrs["Unit"] = "TECU"
dTEC4530.attrs["Description"] = "dTEC from TOW-45 to TOW-30."
dTEC4530.attrs["Unit"] = "TECU"
TEC15.attrs["Description"] = "TEC at TOW-15 sec, with calibration."
TEC15.attrs["Unit"] = "TECU"
dTEC3015.attrs["Description"] = "dTEC from TOW-30 to TOW-15."
dTEC3015.attrs["Unit"] = "TECU"
TECtow.attrs["Description"] = "TEC at TOW, with calibration."
TECtow.attrs["Unit"] = "TECU"
dTEC15tow.attrs["Description"] = "dTEC from TOW-15 to TOW."
dTEC15tow.attrs["Unit"] = "TECU"
locktTEC.attrs["Description"] = "Lock time on second frequency used for TEC computation."
locktTEC.attrs["Unit"] = "Seconds"

CN0TEC.attrs["Description"] = "Average C/N0 of seconde frequency used for TEC computation."
CN0TEC.attrs["Unit"] = "dB-Hz"


# Assign hourly readings

for i in range(0, len(ismrfile)):

    GPSweek[i] = int(ismrfile['GPSweek'][i])
    TOW[i] = int(ismrfile['TOW'][i])
    UNIXTime[i] = int(unixTime[i])
    SVID[i] = int(ismrfile['sv'][i])
    Azimuth[i] = float(ismrfile['Azimuth'][i])
    Elevation[i] = float(ismrfile['Elevation'][i])
    Longitude[i] = float(lonIPP[i])
    Latitude[i] = float(latIPP[i])
    Sept_Rxstate[i] = int(ismrfile['Rxstate'][i])
    Sept_sbf2ismrversion[i] = int(ismrfile['sbfver'][i])
    
    AvgCN0s1[i] = float(ismrfile['AvgCN0s1'][i])
    S4s1[i] = float(ismrfile['S4s1'][i])
    S4cors1[i] = float(ismrfile['S4cors1'][i])
    Phi01s1[i] = float(ismrfile['Phi01s1'][i])
    Phi03s1[i] = float(ismrfile['Phi03s1'][i])
    Phi10s1[i] = float(ismrfile['Phi10s1'][i])
    Phi30s1[i] = float(ismrfile['Phi30s1'][i])
    Phi60s1[i] = float(ismrfile['Phi60s1'][i])
    AvgCCDs1[i] = float(ismrfile['AvgCCDs1'][i])
    SigmaCCDs1[i] = float(ismrfile['SigmaCCDs1'][i])
    lockts1[i] = float(ismrfile['lockts1'][i])
    SIs1[i] = float(ismrfile['SIs1'][i])
    SInums1[i] = float(ismrfile['SInums1'][i])
    ps1[i] = float(ismrfile['ps1'][i])
    Ts1 = float(ismrfile['Ts1'][i])
    
    AvgCN0s2[i] = float(ismrfile['AvgCN0s2'][i])
    S4s2[i] = float(ismrfile['S4s2'][i])
    S4cors2[i] = float(ismrfile['S4cors2'][i])
    Phi01s2[i] = float(ismrfile['Phi01s2'][i])
    Phi03s2[i] = float(ismrfile['Phi03s2'][i])
    Phi10s2[i] = float(ismrfile['Phi10s2'][i])
    Phi30s2[i] = float(ismrfile['Phi30s2'][i])
    Phi60s2[i] = float(ismrfile['Phi60s2'][i])
    AvgCCDs2[i] = float(ismrfile['AvgCCDs2'][i])
    SigmaCCDs2[i] = float(ismrfile['SigmaCCDs2'][i])
    lockts2[i] = float(ismrfile['lockts2'][i])
    SIs2[i] = float(ismrfile['SIs2'][i])
    SInums2[i] = float(ismrfile['SInums2'][i])
    ps2[i] = float(ismrfile['ps2'][i])
    Ts2 = float(ismrfile['Ts2'][i])
    
    AvgCN0s3[i] = float(ismrfile['AvgCN0s3'][i])
    S4s3[i] = float(ismrfile['S4s3'][i])
    S4cors3[i] = float(ismrfile['S4cors3'][i])
    Phi01s3[i] = float(ismrfile['Phi01s3'][i])
    Phi03s3[i] = float(ismrfile['Phi03s3'][i])
    Phi10s3[i] = float(ismrfile['Phi10s3'][i])
    Phi30s3[i] = float(ismrfile['Phi30s3'][i])
    Phi60s3[i] = float(ismrfile['Phi60s3'][i])
    AvgCCDs3[i] = float(ismrfile['AvgCCDs3'][i])
    SigmaCCDs3[i] = float(ismrfile['SigmaCCDs3'][i])
    lockts3[i] = float(ismrfile['lockts3'][i])
    SIs3[i] = float(ismrfile['SIs3'][i])
    SInums3[i] = float(ismrfile['SInums3'][i])
    ps3[i] = float(ismrfile['ps3'][i])
    Ts3 = float(ismrfile['Ts3'][i])
    
    TEC45[i] = float(ismrfile['TEC45'][i])
    dTEC6045[i] = float(ismrfile['dTEC6045'][i])
    TEC30[i] = float(ismrfile['TEC30'][i])
    dTEC4530[i] = float(ismrfile['dTEC4530'][i])
    TEC15[i] = float(ismrfile['TEC15'][i])
    dTEC3015[i] = float(ismrfile['dTEC3015'][i])
    TECtow[i] = float(ismrfile['TECtow'][i])
    dTEC15tow[i] = float(ismrfile['dTEC15tow'][i])
    locktTEC[i] = float(ismrfile['Phi01s1'][i])
    
    CN0TEC[i] = float(ismrfile['CN0TEC'][i])
    
# dimension scales
hdf5File['UNIXTime'].make_scale()


hdf5File["GPSweek"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["TOW"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SVID"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Azimuth"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Elevation"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Longitude"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Latitude"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Sept_Rxstate"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Sept_sbf2ismrversion"].dims[0].attach_scale(hdf5File['UNIXTime'])

hdf5File["AvgCN0s1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["S4s1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["S4cors1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi01s1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi03s1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi10s1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi30s1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi60s1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["AvgCCDs1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SigmaCCDs1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["lockts1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SIs1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SInums1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["ps1"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Ts1"].dims[0].attach_scale(hdf5File['UNIXTime'])

hdf5File["AvgCN0s2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["S4s2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["S4cors2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi01s2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi03s2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi10s2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi30s2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi60s2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["AvgCCDs2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SigmaCCDs2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["lockts2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SIs2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SInums2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["ps2"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Ts2"].dims[0].attach_scale(hdf5File['UNIXTime'])

hdf5File["AvgCN0s3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["S4s3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["S4cors3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi01s3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi03s3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi10s3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi30s3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Phi60s3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["AvgCCDs3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SigmaCCDs3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["lockts3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SIs3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["SInums3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["ps3"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["Ts3"].dims[0].attach_scale(hdf5File['UNIXTime'])

hdf5File["TEC45"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["dTEC6045"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["TEC30"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["dTEC4530"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["TEC15"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["dTEC3015"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["TECtow"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["dTEC15tow"].dims[0].attach_scale(hdf5File['UNIXTime'])
hdf5File["locktTEC"].dims[0].attach_scale(hdf5File['UNIXTime'])

hdf5File["CN0TEC"].dims[0].attach_scale(hdf5File['UNIXTime'])


hdf5File.close()
