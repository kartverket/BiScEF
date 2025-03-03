import os
import sys
import argparse
import configparser
import csv
import datetime
import math
import pandas as pd
import h5py
import numpy as np


# Function to read configuration file
def read_config(fname:str):
	if os.path.exists(f'{fname}') == False:
		print("ERROR: Failed to read configuration file \"" + fname + "\"")
		return False
	config = configparser.ConfigParser()
	with open(fname) as f:
		file_content = '[root]\n' + f.read()
	config.read_string(file_content)
	config_values = {
		'PhaseHighPassFilterFreqCutoff': config.getfloat('root', 'PhaseHighPassFilterFreqCutoff'),
		'PhaseHighPassFilterType': config.get('root', 'PhaseHighPassFilterType'),
		'ElevationCutoff': config.getfloat('root', 'ElevationCutoff'),   # Note: This is not used for filtering in this script.
		'Constellations': config.get('root', 'Constellations'),
		'SignalStatement': config.get('root', 'SignalStatement'),
		'SLMHeight': config.getfloat('root', 'SLMHeight'),
		'Agency': config.get('root', 'Agency'),
		'Contact': config.get('root', 'Contact'),
		'DOI': config.get('root', 'DOI'),
		'License': config.get('root', 'License'),
		'Comment': config.get('root', 'Comment'),
		'ReceiverInfoFile' : config.get('root', 'ReceiverInfoFile'),
		'Varnames' : config.get('root', 'Varnames')
	}
	return config_values


# Function to load data files
def load_data(filenames:list, station:str):

	# Define data structure
	#  Default Septentrio:
	varnames = ['GPSWeek','TOW','sv','Rxstate','Azimuth','Elevation',
		'AvgCN0s1','S4s1','S4cors1','Phi01s1','Phi03s1','Phi10s1',
		'Phi30s1','Phi60s1','AvgCCDs1','SigmaCCDs1','TEC45','dTEC6045',
		'TEC30','dTEC4530','TEC15','dTEC3015','TECtow','dTEC15tow',
		'lockts1','sbfver','locktTEC','CN0TEC','SIs1','SInums1','ps1',
		'AvgCN0s2','S4s2','S4cors2','Phi01s2','Phi03s2','Phi10s2',
		'Phi30s2','Phi60s2','AvgCCDs2','SigmaCCDs2','lockts2','SIs2',
		'SInums2','ps2','AvgCN0s3','S4s3','S4cors3','Phi01s3',
		'Phi03s3','Phi10s3','Phi30s3','Phi60s3','AvgCCDs3',
		'SigmaCCDs3','lockts3','SIs3','SInums3','ps3','Ts1','Ts2','Ts3']
	#  If set in config file, replace default:
	if(len(config['Varnames']) > 0):
		varnames = config['Varnames'].split(',')
	#  Prepare data frame
	data = pd.DataFrame(columns = varnames)

	# Load data
	for fname in filenames:
		if os.path.exists(f'{fname}') == True:
			if ".gz" in fname == True:
				datatemp = pd.read_csv(f'{fname}', compression='gzip', names=varnames)
			else:
				datatemp = pd.read_csv(f'{fname}', names=varnames)
			data = pd.concat([data, datatemp], axis=0, ignore_index=True)
			
	# Check for minimum required columns
	if (not 'GPSWeek' in data) or (len(data.GPSWeek) == 0):
		print("ERROR: No GPSWeek in data.")
		return False
	if (not 'TOW' in data) or (len(data.TOW) == 0):
		print("ERROR: No TOW in data.")
		return False
	if (not 'Azimuth' in data) or (len(data.Azimuth) == 0):
		print("ERROR: No Azimuth in data.")
		return False
	if (not 'Elevation' in data) or (len(data.Elevation) == 0):
		print("ERROR: No Elevation in data.")
		return False

	# Drop rows where the 'GPSWeek' column is not a numeric value. This is intended to purge header lines loaded from files where those were present.
	if(type(data['GPSWeek'][0]) == str):
		data = data[data['GPSWeek'].str.isnumeric()].reset_index()

	# Make conversions as necessary - for integer columns
	convert_dict = {'UNIXTime': np.int64,
			'GPSWeek': np.int32,
			'TOW': np.int32,
			'sv': np.int32,
			'Rxstate': np.int32,
			'GPSWeek': np.int32,
			'lockts1': np.int32,
			'lockts2': np.int32,
			'lockts3': np.int32,
			'locktTEC': np.int32
			}
	for k in convert_dict:
		if k in data:
			data[k] = pd.to_numeric(data[k], errors='coerce').fillna(0).astype(convert_dict[k])

	# Make conversions as necessary - for float columns 
	for k in varnames:
		if k not in convert_dict:   # (all columns that are not integer are floats)
			if k in data:
				data[k] = pd.to_numeric(data[k], errors='coerce').astype(np.float32)

	# Make timestamps
	gpsEpoch = datetime.datetime(1980,1,6,0,0,0, tzinfo=datetime.timezone.utc)
	unixEpoch = datetime.datetime(1970,1,1,0,0,0, tzinfo=datetime.timezone.utc)
	leapSecDiff = datetime.timedelta(seconds=9) #leap seconds between 1970-1-1 (unix epoch) and  1980-1-6 (GPS epoch)
	UNIXTime_datetimes = (gpsEpoch - unixEpoch + leapSecDiff) + pd.to_timedelta(data.GPSWeek*7, unit='days') + pd.to_timedelta(data.TOW, unit='second')
	data['UNIXTime'] = [x.total_seconds() for x in UNIXTime_datetimes]
	data['UNIXTime'] = data['UNIXTime'].astype(np.int64)

	# Calculate IPPs
	lon_r = float(receiver[cmdOpts['recCode']]['ReceiverLongitude'])
	lat_r = float(receiver[cmdOpts['recCode']]['ReceiverLatitude'])
	d2r = math.pi/180
	r2d = 1 / d2r
	el = data['Elevation'].values * d2r
	az = data['Azimuth'].values * d2r
	Re = 6378137   # WGS-84 semi-major axis
	Hip = config['SLMHeight']
	Gamma = [0]*len(el)
	lat_ip = [0]*len(el)
	lon_ip = [0]*len(el)
	for i in range(0, len(el)):
		Gamma[i] = (math.pi/2) - el[i] - math.asin((Re / (Re + Hip)) * math.cos(el[i]))
		lat_ip[i] = math.asin(math.sin(lat_r * d2r) * math.cos(Gamma[i]) + math.cos(lat_r * d2r) * math.sin(Gamma[i]) * math.cos(az[i])) * r2d
		lon_ip[i] = lon_r + math.asin(math.sin(Gamma[i]) * math.sin(az[i]) / math.cos(lat_ip[i] * d2r)) * r2d
	data['Longitude'] = lon_ip
	data['Latitude'] = lat_ip
	data['Longitude'] = data['Longitude'].astype(np.float32)
	data['Latitude'] = data['Latitude'].astype(np.float32)
				
	return data
	


# Input from command line
parser = argparse.ArgumentParser(description="ismr to BiScEF converter",
				 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
				 epilog="NB: This script assumes that the file contains data from one day (or less), in chronological order. The output file name will be based on the first timetag encountered in the data.")
parser.add_argument("--config", type=str, default="Info.cfg", help="Filename of configuration file")
parser.add_argument("--recCode", type=str, default="XXXX", required=True, help="Receiver code for the receiver that produced the input data file(s)")
parser.add_argument("--outputPath", type=str, default="./", help="Path in which to save the output data file(s)")
parser.add_argument("filename", nargs="+", help="Filename(s) of input data file(s)")
args = parser.parse_args()
cmdOpts = vars(args)


# Read configuration file
config = read_config(cmdOpts['config'])
if type(config) is bool:   # (If this happens, the config read failed.)
	exit(1)
with open(config['ReceiverInfoFile']) as f:
	fr = csv.DictReader(f)
	receiver = dict()
	for row in fr:
		receiver[row['RecCode']] = row

# Load data file(s)
data_in = load_data(cmdOpts['filename'], cmdOpts['recCode'])
if type(data_in) is bool:   # (If this happens, the data read failed.)
	exit(1)
if len(data_in) == 0:
	print("ERROR: No data loaded.")
	exit(2)


# Create a HDF5 file
date = datetime.datetime.fromtimestamp(data_in['UNIXTime'][0], datetime.timezone.utc)
country = receiver[cmdOpts['recCode']]['CountryCode'].upper()
recCode = cmdOpts['recCode'].upper()
year = '{:04d}'.format(date.year)
month = '{:02d}'.format(date.month)
day = '{:02d}'.format(date.day)
fileOpenMode	= "w";
hdfFileName	 = os.path.join(cmdOpts['outputPath'], f"{country}{recCode}{year}{month}{day}.nc")
hdf5File		= h5py.File(hdfFileName, fileOpenMode);


## Attributes at root level

hdf5File.attrs["BiScEFVersion"] = "1.1"
hdf5File.attrs["ReceiverType"] = receiver[cmdOpts['recCode']]['ReceiverType']
if len(receiver[cmdOpts['recCode']]['ReceiverFWVersion']) > 0:
	hdf5File.attrs["ReceiverFWVersion"] = receiver[cmdOpts['recCode']]['ReceiverFWVersion']
hdf5File.attrs["ReceiverCode"] = cmdOpts['recCode']
hdf5File.attrs["ReceiverLongitude"] = float(receiver[cmdOpts['recCode']]['ReceiverLongitude'])
hdf5File.attrs["ReceiverLatitude"] = float(receiver[cmdOpts['recCode']]['ReceiverLatitude'])
if len(receiver[cmdOpts['recCode']]['ReceiverHeight']) > 0:
	hdf5File.attrs["ReceiverHeight"] = float(receiver[cmdOpts['recCode']]['ReceiverHeight'])
#if len(receiver[cmdOpts['recCode']]['ReceiverCoord_x']) > 0:
#	hdf5File.attrs["Coordinate"] = How do I constract that in python? hmmm...
hdf5File.attrs["ReceiverSamplingRate"] = float(receiver[cmdOpts['recCode']]['ReceiverSamplingRate'])
hdf5File.attrs["AntennaType"] = receiver[cmdOpts['recCode']]['AntennaType']
if len(receiver[cmdOpts['recCode']]['AntennaSerialNo']) > 0:
	hdf5File.attrs["AntennaSerialNo"] = receiver[cmdOpts['recCode']]['AntennaSerialNo']

hdf5File.attrs["Constellations"] = config['Constellations']
hdf5File.attrs["SignalStatement"] = config['SignalStatement']
hdf5File.attrs["PhaseHighPassFilterFreqCutoff"] = config['PhaseHighPassFilterFreqCutoff']
hdf5File.attrs["PhaseHighPassFilterType"] = config['PhaseHighPassFilterType']
hdf5File.attrs["ElevationCutoff"] = config['ElevationCutoff']
hdf5File.attrs["SLMHeight"] = config['SLMHeight']

if len(config['Agency']) > 0:
	hdf5File.attrs["Agency"] = config['Agency']
if len(receiver[cmdOpts['recCode']]['CountryCode']) > 0:
	hdf5File.attrs["Country"] = receiver[cmdOpts['recCode']]['CountryCode']
if len(config['Contact']) > 0:
	hdf5File.attrs["Contact"] = config['Contact']
if len(config['DOI']) > 0:
	hdf5File.attrs["DOI"] = config['DOI']
if len(config['License']) > 0:
	hdf5File.attrs["License"] = config['License']
if len(config['Comment']) > 0:
	hdf5File.attrs["Comment"] = config['Comment']


## Datasets

UNIXTime = hdf5File.create_dataset("UNIXTime", data=data_in['UNIXTime'], compression="gzip")
UNIXTime.attrs["Description"] = "Seconds since Jan 01 1970 UTC."
UNIXTime.attrs["Unit"] = "Seconds"
hdf5File['UNIXTime'].make_scale()

GPSWeek = hdf5File.create_dataset("GPSWeek", data=data_in['GPSWeek'], compression="gzip")
GPSWeek.attrs["Description"] = "GPS week number since 06 January 1980. The weeks run from Sunday to Saturday."
GPSWeek.attrs["Unit"] = "Week"
hdf5File["GPSWeek"].dims[0].attach_scale(hdf5File['UNIXTime'])

TOW = hdf5File.create_dataset("TOW", data=data_in['TOW'], compression="gzip")
TOW.attrs["Description"] = "The second of the week starting from Sunday"
TOW.attrs["Unit"] = "Seconds"
hdf5File["TOW"].dims[0].attach_scale(hdf5File['UNIXTime'])

SVID = hdf5File.create_dataset("SVID", data=data_in['sv'], compression="gzip")
SVID.attrs["Description"] = "Satellite vehicle ID"
hdf5File["SVID"].dims[0].attach_scale(hdf5File['UNIXTime'])

Azimuth = hdf5File.create_dataset("Azimuth", data=data_in['Azimuth'], compression="gzip")
Azimuth.attrs["Description"] = "Azimuth of satellite."
Azimuth.attrs["Unit"] = "Degrees"
hdf5File["Azimuth"].dims[0].attach_scale(hdf5File['UNIXTime'])

Elevation = hdf5File.create_dataset("Elevation", data=data_in['Elevation'], compression="gzip")
Elevation.attrs["Description"] = "Elevation of satellite."
Elevation.attrs["Unit"] = "Degrees"
hdf5File["Elevation"].dims[0].attach_scale(hdf5File['UNIXTime'])

Longitude = hdf5File.create_dataset("Longitude", data=data_in['Longitude'], compression="gzip")
Longitude.attrs["Description"] = "Longitude of the Ionospheric Pierce Point (IPP)."
Longitude.attrs["Unit"] = "Degrees East"
hdf5File["Longitude"].dims[0].attach_scale(hdf5File['UNIXTime'])

Latitude = hdf5File.create_dataset("Latitude", data=data_in['Latitude'], compression="gzip")
Latitude.attrs["Description"] = "Latitude of the Ionospheric Pierce Point (IPP)."
Latitude.attrs["Unit"] = "Degrees North"
hdf5File["Latitude"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Rxstate' in data_in:
	Sept_Rxstate = hdf5File.create_dataset("Sept_Rxstate", data=data_in['Rxstate'], compression="gzip")
	Sept_Rxstate.attrs["Description"] = "Value of the RxState field of the ReceiverStatus SBF block."
	hdf5File["Sept_Rxstate"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'sbfver' in data_in:
	Sept_sbf2ismrversion = hdf5File.create_dataset("Sept_sbf2ismrversion", data=data_in['sbfver'], compression="gzip")
	Sept_sbf2ismrversion.attrs["Description"] = "sbf2ismr version number."
	hdf5File["Sept_sbf2ismrversion"].dims[0].attach_scale(hdf5File['UNIXTime'])


if 'AvgCN0s1' in data_in:
	AvgCN0s1 = hdf5File.create_dataset("AvgCN0s1", data=data_in['AvgCN0s1'], compression="gzip")
	AvgCN0s1.attrs["Description"] = "Average signal 1 C/N0 over the last minute."
	AvgCN0s1.attrs["Unit"] = "dB-Hz"
	hdf5File["AvgCN0s1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'S4s1' in data_in:
	S4s1 = hdf5File.create_dataset("S4s1", data=data_in['S4s1'], compression="gzip")
	S4s1.attrs["Description"] = "Corrected S4 on signal 1."
	hdf5File["S4s1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'S4cors1' in data_in:
	S4cors1 = hdf5File.create_dataset("S4cors1", data=data_in['S4cors1'], compression="gzip")
	S4cors1.attrs["Description"] = "Correction to total S4 on signal 1."
	hdf5File["S4cors1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi01s1' in data_in:
	data_in.loc[data_in['Phi01s1'] > 2, 'Phi01s1'] = np.nan  # Assume all values above 2 radians are errors and replace them with nan
	Phi01s1 = hdf5File.create_dataset("Phi01s1", data=data_in['Phi01s1'], compression="gzip")
	Phi01s1.attrs["Description"] = "1-second phase sigma on signal 1."
	Phi01s1.attrs["Unit"] = "Radians"
	hdf5File["Phi01s1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi03s1' in data_in:
	data_in.loc[data_in['Phi03s1'] > 2, 'Phi03s1'] = np.nan  # Assume all values above 2 radians are errors and replace them with nan
	Phi03s1 = hdf5File.create_dataset("Phi03s1", data=data_in['Phi03s1'], compression="gzip")
	Phi03s1.attrs["Description"] = "3-second phase sigma on signal 1."
	Phi03s1.attrs["Unit"] = "Radians"
	hdf5File["Phi03s1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi10s1' in data_in:
	data_in.loc[data_in['Phi10s1'] > 2, 'Phi10s1'] = np.nan  # Assume all values above 2 radians are errors and replace them with nan
	Phi10s1= hdf5File.create_dataset("Phi10s1", data=data_in['Phi10s1'], compression="gzip")
	Phi10s1.attrs["Description"] = "10-second phase sigma on signal 1."
	Phi10s1.attrs["Unit"] = "Radians"
	hdf5File["Phi10s1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi30s1' in data_in:
	data_in.loc[data_in['Phi30s1'] > 2, 'Phi30s1'] = np.nan  # Assume all values above 2 radians are errors and replace them with nan
	Phi30s1 = hdf5File.create_dataset("Phi30s1", data=data_in['Phi30s1'], compression="gzip")
	Phi30s1.attrs["Description"] = "30-second phase sigma on signal 1."
	Phi30s1.attrs["Unit"] = "Radians"
	hdf5File["Phi30s1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi60s1' in data_in:
	data_in.loc[data_in['Phi60s1'] > 2, 'Phi60s1'] = np.nan  # Assume all values above 2 radians are errors and replace them with nan
	Phi60s1 = hdf5File.create_dataset("Phi60s1", data=data_in['Phi60s1'], compression="gzip")
	Phi60s1.attrs["Description"] = "60-second phase sigma on signal 1."
	Phi60s1.attrs["Unit"] = "Radians"
	hdf5File["Phi60s1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'AvgCCDs1' in data_in:
	AvgCCDs1 = hdf5File.create_dataset("AvgCCDs1", data=data_in['AvgCCDs1'], compression="gzip")
	AvgCCDs1.attrs["Description"] = "Average code-carrier divergence for signal 1."
	AvgCCDs1.attrs["Unit"] = "Meters"
	hdf5File["AvgCCDs1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'SigmaCCDs1' in data_in:
	SigmaCCDs1 = hdf5File.create_dataset("SigmaCCDs1", data=data_in['SigmaCCDs1'], compression="gzip")
	SigmaCCDs1.attrs["Description"] = "Standard deviation of code-carrier divergence for signal 1."
	SigmaCCDs1.attrs["Unit"] = "Meters"
	hdf5File["SigmaCCDs1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'lockts1' in data_in:
	lockts1 = hdf5File.create_dataset("lockts1", data=data_in['lockts1'], compression="gzip")
	lockts1.attrs["Description"] = "Signal lock time for signal 1."
	lockts1.attrs["Unit"] = "Seconds"
	hdf5File["lockts1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'SIs1' in data_in:
	SIs1 = hdf5File.create_dataset("SIs1", data=data_in['SIs1'], compression="gzip")
	SIs1.attrs["Description"] = "SI index on signal 1"
	hdf5File["SIs1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'SInums1' in data_in:
	SInums1 = hdf5File.create_dataset("SInums1", data=data_in['SInums1'], compression="gzip")
	SInums1.attrs["Description"] = "Numerator of SI index on signal 1"
	hdf5File["SInums1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'ps1' in data_in:
	ps1 = hdf5File.create_dataset("ps1", data=data_in['ps1'], compression="gzip")
	ps1.attrs["Description"] = "Spectral slope for detrended phase in the 0.1 to 25 Hz range for signal 1"
	hdf5File["ps1"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Ts1' in data_in:
	Ts1 = hdf5File.create_dataset("Ts1", data=data_in['Ts1'], compression="gzip")
	Ts1.attrs["Description"] = "Phase power spectral density at 1 Hz on signal 1."
	Ts1.attrs["Unit"] = "Radians^2/Hz"
	hdf5File["Ts1"].dims[0].attach_scale(hdf5File['UNIXTime'])


if 'AvgCN0s2' in data_in:
	AvgCN0s2 = hdf5File.create_dataset("AvgCN0s2", data=data_in['AvgCN0s2'], compression="gzip")
	AvgCN0s2.attrs["Description"] = "Average signal 2 C/N0 over the last minute."
	AvgCN0s2.attrs["Unit"] = "dB-Hz"
	hdf5File["AvgCN0s2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'S4s2' in data_in:
	S4s2 = hdf5File.create_dataset("S4s2", data=data_in['S4s2'], compression="gzip")
	S4s2.attrs["Description"] = "Corrected S4 on signal 2."
	hdf5File["S4s2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'S4cors2' in data_in:
	S4cors2 = hdf5File.create_dataset("S4cors2", data=data_in['S4cors2'], compression="gzip")
	S4cors2.attrs["Description"] = "Correction to total S4 on signal 2."
	hdf5File["S4cors2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi01s2' in data_in:
	Phi01s2 = hdf5File.create_dataset("Phi01s2", data=data_in['Phi01s2'], compression="gzip")
	Phi01s2.attrs["Description"] = "1-second phase sigma on signal 2."
	Phi01s2.attrs["Unit"] = "Radians"
	hdf5File["Phi01s2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi03s2' in data_in:
	Phi03s2 = hdf5File.create_dataset("Phi03s2", data=data_in['Phi03s2'], compression="gzip")
	Phi03s2.attrs["Description"] = "3-second phase sigma on signal 2."
	Phi03s2.attrs["Unit"] = "Radians"
	hdf5File["Phi03s2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi10s2' in data_in:
	Phi10s2= hdf5File.create_dataset("Phi10s2", data=data_in['Phi10s2'], compression="gzip")
	Phi10s2.attrs["Description"] = "10-second phase sigma on signal 2."
	Phi10s2.attrs["Unit"] = "Radians"
	hdf5File["Phi10s2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi30s2' in data_in:
	Phi30s2 = hdf5File.create_dataset("Phi30s2", data=data_in['Phi30s2'], compression="gzip")
	Phi30s2.attrs["Description"] = "30-second phase sigma on signal 2."
	Phi30s2.attrs["Unit"] = "Radians"
	hdf5File["Phi30s2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi60s2' in data_in:
	Phi60s2 = hdf5File.create_dataset("Phi60s2", data=data_in['Phi60s2'], compression="gzip")
	Phi60s2.attrs["Description"] = "60-second phase sigma on signal 2."
	Phi60s2.attrs["Unit"] = "Radians"
	hdf5File["Phi60s2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'AvgCCDs2' in data_in:
	AvgCCDs2 = hdf5File.create_dataset("AvgCCDs2", data=data_in['AvgCCDs2'], compression="gzip")
	AvgCCDs2.attrs["Description"] = "Average code-carrier divergence for signal 2."
	AvgCCDs2.attrs["Unit"] = "Meters"
	hdf5File["AvgCCDs2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'SigmaCCDs2' in data_in:
	SigmaCCDs2 = hdf5File.create_dataset("SigmaCCDs2", data=data_in['SigmaCCDs2'], compression="gzip")
	SigmaCCDs2.attrs["Description"] = "Standard deviation of code-carrier divergence for signal 2."
	SigmaCCDs2.attrs["Unit"] = "Meters"
	hdf5File["SigmaCCDs2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'lockts2' in data_in:
	lockts2 = hdf5File.create_dataset("lockts2", data=data_in['lockts2'], compression="gzip")
	lockts2.attrs["Description"] = "Signal lock time for signal 2."
	lockts2.attrs["Unit"] = "Seconds"
	hdf5File["lockts2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'SIs2' in data_in:
	SIs2 = hdf5File.create_dataset("SIs2", data=data_in['SIs2'], compression="gzip")
	SIs2.attrs["Description"] = "SI index on signal 2"
	hdf5File["SIs2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'SInums2' in data_in:
	SInums2 = hdf5File.create_dataset("SInums2", data=data_in['SInums2'], compression="gzip")
	SInums2.attrs["Description"] = "Numerator of SI index on signal 2"
	hdf5File["SInums2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'ps2' in data_in:
	ps2 = hdf5File.create_dataset("ps2", data=data_in['ps2'], compression="gzip")
	ps2.attrs["Description"] = "Spectral slope for detrended phase in the 0.1 to 25 Hz range for signal 2"
	hdf5File["ps2"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Ts2' in data_in:
	Ts2 = hdf5File.create_dataset("Ts2", data=data_in['Ts2'], compression="gzip")
	Ts2.attrs["Description"] = "Phase power spectral density at 1 Hz on signal 2."
	Ts2.attrs["Unit"] = "Radians^2/Hz"
	hdf5File["Ts2"].dims[0].attach_scale(hdf5File['UNIXTime'])


if 'AvgCN0s3' in data_in:
	AvgCN0s3 = hdf5File.create_dataset("AvgCN0s3", data=data_in['AvgCN0s3'], compression="gzip")
	AvgCN0s3.attrs["Description"] = "Average signal 3 C/N0 over the last minute."
	AvgCN0s3.attrs["Unit"] = "dB-Hz"
	hdf5File["AvgCN0s3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'S4s3' in data_in:
	S4s3 = hdf5File.create_dataset("S4s3", data=data_in['S4s3'], compression="gzip")
	S4s3.attrs["Description"] = "Corrected S4 on signal 3."
	hdf5File["S4s3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'S4cors3' in data_in:
	S4cors3 = hdf5File.create_dataset("S4cors3", data=data_in['S4cors3'], compression="gzip")
	S4cors3.attrs["Description"] = "Correction to total S4 on signal 3."
	hdf5File["S4cors3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi01s3' in data_in:
	Phi01s3 = hdf5File.create_dataset("Phi01s3", data=data_in['Phi01s3'], compression="gzip")
	Phi01s3.attrs["Description"] = "1-second phase sigma on signal 3."
	Phi01s3.attrs["Unit"] = "Radians"
	hdf5File["Phi01s3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi03s3' in data_in:
	Phi03s3 = hdf5File.create_dataset("Phi03s3", data=data_in['Phi03s3'], compression="gzip")
	Phi03s3.attrs["Description"] = "3-second phase sigma on signal 3."
	Phi03s3.attrs["Unit"] = "Radians"
	hdf5File["Phi03s3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi10s3' in data_in:
	Phi10s3= hdf5File.create_dataset("Phi10s3", data=data_in['Phi10s3'], compression="gzip")
	Phi10s3.attrs["Description"] = "10-second phase sigma on signal 3."
	Phi10s3.attrs["Unit"] = "Radians"
	hdf5File["Phi10s3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi30s3' in data_in:
	Phi30s3 = hdf5File.create_dataset("Phi30s3", data=data_in['Phi30s3'], compression="gzip")
	Phi30s3.attrs["Description"] = "30-second phase sigma on signal 3."
	Phi30s3.attrs["Unit"] = "Radians"
	hdf5File["Phi30s3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Phi60s3' in data_in:
	Phi60s3 = hdf5File.create_dataset("Phi60s3", data=data_in['Phi60s3'], compression="gzip")
	Phi60s3.attrs["Description"] = "60-second phase sigma on signal 3."
	Phi60s3.attrs["Unit"] = "Radians"
	hdf5File["Phi60s3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'AvgCCDs3' in data_in:
	AvgCCDs3 = hdf5File.create_dataset("AvgCCDs3", data=data_in['AvgCCDs3'], compression="gzip")
	AvgCCDs3.attrs["Description"] = "Average code-carrier divergence for signal 3."
	AvgCCDs3.attrs["Unit"] = "Meters"
	hdf5File["AvgCCDs3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'SigmaCCDs3' in data_in:
	SigmaCCDs3 = hdf5File.create_dataset("SigmaCCDs3", data=data_in['SigmaCCDs3'], compression="gzip")
	SigmaCCDs3.attrs["Description"] = "Standard deviation of code-carrier divergence for signal 3."
	SigmaCCDs3.attrs["Unit"] = "Meters"
	hdf5File["SigmaCCDs3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'lockts3' in data_in:
	lockts3 = hdf5File.create_dataset("lockts3", data=data_in['lockts3'], compression="gzip")
	lockts3.attrs["Description"] = "Signal lock time for signal 3."
	lockts3.attrs["Unit"] = "Seconds"
	hdf5File["lockts3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'SIs3' in data_in:
	SIs3 = hdf5File.create_dataset("SIs3", data=data_in['SIs3'], compression="gzip")
	SIs3.attrs["Description"] = "SI index on signal 3"
	hdf5File["SIs3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'SInums3' in data_in:
	SInums3 = hdf5File.create_dataset("SInums3", data=data_in['SInums3'], compression="gzip")
	SInums3.attrs["Description"] = "Numerator of SI index on signal 3"
	hdf5File["SInums3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'ps3' in data_in:
	ps3 = hdf5File.create_dataset("ps3", data=data_in['ps3'], compression="gzip")
	ps3.attrs["Description"] = "Spectral slope for detrended phase in the 0.1 to 25 Hz range for signal 3"
	hdf5File["ps3"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'Ts3' in data_in:
	Ts3 = hdf5File.create_dataset("Ts3", data=data_in['Ts3'], compression="gzip")
	Ts3.attrs["Description"] = "Phase power spectral density at 1 Hz on signal 3."
	Ts3.attrs["Unit"] = "Radians^2/Hz"
	hdf5File["Ts3"].dims[0].attach_scale(hdf5File['UNIXTime'])


if 'TEC45' in data_in:
	TEC45 = hdf5File.create_dataset("TEC45", data=data_in['TEC45'], compression="gzip")
	TEC45.attrs["Description"] = "TEC at TOW-45 sec, with calibration."
	TEC45.attrs["Unit"] = "TECU"
	hdf5File["TEC45"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'dTEC6045' in data_in:
	dTEC6045 = hdf5File.create_dataset("dTEC6045", data=data_in['dTEC6045'], compression="gzip")
	dTEC6045.attrs["Description"] = "dTEC from TOW-60 to TOW-45."
	dTEC6045.attrs["Unit"] = "TECU"
	hdf5File["dTEC6045"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'TEC30' in data_in:
	TEC30 = hdf5File.create_dataset("TEC30", data=data_in['TEC30'], compression="gzip")
	TEC30.attrs["Description"] = "TEC at TOW-30 sec, with calibration."
	TEC30.attrs["Unit"] = "TECU"
	hdf5File["TEC30"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'dTEC4530' in data_in:
	dTEC4530 = hdf5File.create_dataset("dTEC4530", data=data_in['dTEC4530'], compression="gzip")
	dTEC4530.attrs["Description"] = "dTEC from TOW-45 to TOW-30."
	dTEC4530.attrs["Unit"] = "TECU"
	hdf5File["dTEC4530"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'TEC15' in data_in:
	TEC15 = hdf5File.create_dataset("TEC15", data=data_in['TEC15'], compression="gzip")
	TEC15.attrs["Description"] = "TEC at TOW-15 sec, with calibration."
	TEC15.attrs["Unit"] = "TECU"
	hdf5File["TEC15"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'dTEC3015' in data_in:
	dTEC3015 = hdf5File.create_dataset("dTEC3015", data=data_in['dTEC3015'], compression="gzip")
	dTEC3015.attrs["Description"] = "dTEC from TOW-30 to TOW-15."
	dTEC3015.attrs["Unit"] = "TECU"
	hdf5File["dTEC3015"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'TECtow' in data_in:
	TECtow = hdf5File.create_dataset("TECtow", data=data_in['TECtow'], compression="gzip")
	TECtow.attrs["Description"] = "TEC at TOW, with calibration."
	TECtow.attrs["Unit"] = "TECU"
	hdf5File["TECtow"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'dTEC15tow' in data_in:
	dTEC15tow = hdf5File.create_dataset("dTEC15tow", data=data_in['dTEC15tow'], compression="gzip")
	dTEC15tow.attrs["Description"] = "dTEC from TOW-15 to TOW."
	dTEC15tow.attrs["Unit"] = "TECU"
	hdf5File["dTEC15tow"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'locktTEC' in data_in:
	locktTEC = hdf5File.create_dataset("locktTEC", data=data_in['locktTEC'], compression="gzip")
	locktTEC.attrs["Description"] = "Lock time on second frequency used for TEC computation."
	locktTEC.attrs["Unit"] = "Seconds"
	hdf5File["locktTEC"].dims[0].attach_scale(hdf5File['UNIXTime'])

if 'CN0TEC' in data_in:
	CN0TEC = hdf5File.create_dataset("CN0TEC", data=data_in['CN0TEC'], compression="gzip")
	CN0TEC.attrs["Description"] = "Average C/N0 of seconde frequency used for TEC computation."
	CN0TEC.attrs["Unit"] = "dB-Hz"
	hdf5File["CN0TEC"].dims[0].attach_scale(hdf5File['UNIXTime'])


hdf5File.close()

print("Successfully completed conversion to BiScEF.")
exit(0)


