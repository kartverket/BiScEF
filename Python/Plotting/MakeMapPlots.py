import os
import sys
import h5py    
import numpy as np 
import pandas as pd  
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from itertools import compress
from mpl_toolkits.basemap import Basemap


# Plotting parameters defined per data type
plotParams = { 'Phi60s1':      {'lim': [0, 0.5], 'label': r'Sig1 $\sigma_\phi$', 'hasunit': True,  'canbenegative': False, 'title': 'Phase Scintillation',                     'fnamestr': 'PhaseScint1'},
               'Phi60s2':      {'lim': [0, 0.5], 'label': r'Sig2 $\sigma_\phi$', 'hasunit': True,  'canbenegative': False, 'title': 'Phase Scintillation',                     'fnamestr': 'PhaseScint2'},
               'S4s1':         {'lim': [0, 0.5], 'label': 'Sig1 S4',             'hasunit': False, 'canbenegative': False, 'title': 'Amplitude Scintillation',                 'fnamestr': 'AmpScint1'},
               'S4s2':         {'lim': [0, 0.5], 'label': 'Sig2 S4',             'hasunit': False, 'canbenegative': False, 'title': 'Amplitude Scintillation',                 'fnamestr': 'AmpScint2'},
               'AvgCN0s1':     {               'label': 'Sig1 C/N0',           'hasunit': True,  'canbenegative': False, 'title': 'Carrier/Noise ratio',                       'fnamestr': 'CN01'},
               'AvgCN0s2':     {               'label': 'Sig2 C/N0',           'hasunit': True,  'canbenegative': False, 'title': 'Carrier/Noise ratio',                       'fnamestr': 'CN02'},
               'Ts1':          {               'label': 'Sig1 T',              'hasunit': True,  'canbenegative': False, 'title': 'Phase power spectral density at 1 Hz',      'fnamestr': 'PSDT1Hz'},
               'Ts2':          {               'label': 'Sig2 T',              'hasunit': True,  'canbenegative': False, 'title': 'Phase power spectral density at 1 Hz'},
               'phighs1':      {               'label': 'Sig1 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope', 'legend': '(16 to 25 Hz)', 'fnamestr': 'PSDSlopeParts'},
               'plows1':       {               'label': 'Sig1 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope', 'legend': '(0.1 to 8 Hz)'},
               'pmids1':       {               'label': 'Sig1 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope', 'legend': '(8 to 16 Hz)'},
               'ps1':          {               'label': 'Sig1 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope (0.1 to 25 Hz)',             'fnamestr': 'PSDSlope'},
               'ps2':          {               'label': 'Sig2 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope (0.1 to 25 Hz)'},
               'TECtow':       {               'label': 'TEC',                 'hasunit': True,  'canbenegative': False, 'title': 'TEC',                                       'fnamestr': 'TEC'},
               'TECtow_uncal': {               'label': 'TEC',                 'hasunit': True,  'canbenegative': True,  'title': 'TEC (uncalibrated)',                        'fnamestr': 'uTEC'},
               'ROTI1Hz':      {'lim': [0, 5], 'label': r'ROTI$_{1Hz}$',       'hasunit': True,  'canbenegative': False, 'title': 'ROTI',                                      'fnamestr': 'ROTI'},
               'ROTIFullHz':   {               'label': r'ROTI$_{FullHz}$',    'hasunit': True,  'canbenegative': False, 'title': 'ROTI from full-resolution data',            'fnamestr': 'ROTIf'},
             }
	# (Note: if 'lim' is not defined, plot will auto-scale)


def init_data_storage(datatype):
	global datatypes
	global dataTimes
	global dataValues
	global dataLons
	global dataLats
	global unitStr
	datatypes.append(datatype)
	dataTimes[datatype] = []
	dataValues[datatype] = []
	dataLons[datatype] = []
	dataLats[datatype] = []
	unitStr[datatype] = "?"


def extract_data(const, datatype):
	global dataTimes
	global dataValues
	global dataLons
	global dataLats
	global unitStr
	if not datatype in f.keys():
		return
	if 'Unit' in f[datatype].attrs.keys():
		unitStr[datatype] = f[datatype].attrs['Unit']
	if datatype in f.keys():
		if plotParams[datatype]['canbenegative']:
			hasValue = (f[datatype][()] != 0) & (f[datatype][()] == f[datatype][()])
		else:
			hasValue = (f[datatype][()] > 0) & (f[datatype][()] == f[datatype][()])
		totalFilter = constFilter[const] & hasValue & elevFilter
		if sum(totalFilter) > 0:
			print(" " + str(sum(totalFilter)) + " " + const + " data records loaded.")
			tmp_t = list(compress(f['UNIXTime'][()], totalFilter))
			dataTimes[datatype] = dataTimes[datatype] + [datetime.utcfromtimestamp(t) for t in tmp_t]
			dataValues[datatype] = dataValues[datatype] + list(compress(f[datatype][()], totalFilter))
			dataLons[datatype] = dataLons[datatype] + list(compress(f['Longitude'][()], totalFilter))
			dataLats[datatype] = dataLats[datatype] + list(compress(f['Latitude'][()], totalFilter))



# Make plot - Dots on map
#
# NB: Map settings are set to be suitable for the Norway&Greenland dataset.
#     For other locations, they need to be changed.
#     See https://matplotlib.org/basemap/api/basemap_api.html
#
def plot_map(datatype, values, lons, lats, timeStr, filenameStr):

	plt.clf()
	map = Basemap(width=5000000,height=5000000,projection='laea',resolution=None,lat_ts=70,lat_0=70,lon_0=-10.)
#	map = Basemap(projection='ortho',resolution=None,lat_0=70,lon_0=-10.)   # Showing the globe
	map.shadedrelief()
	x, y = map(lons, lats)
	if 'lim' in plotParams[datatype]:
		plt.scatter(x, y, s=5, c=values, vmin=plotParams[datatype]['lim'][0], vmax=plotParams[datatype]['lim'][1])
	else:
		plt.scatter(x, y, s=5, c=values)
	plt.title(timeStr + ", " + constListStr)

	cb = plt.colorbar()
	if plotParams[datatype]['hasunit']:
		cb.set_label(plotParams[datatype]['label'] + ' (' + unitStr[datatype] + ')')
	else:
		cb.set_label(plotParams[datatype]['label'])
	
	plotfname = filenameStr + '.png'
	plt.savefig(plotfname, dpi=300)
	print("Saved plot to " + plotfname)


# Input from command line:
import argparse
parser = argparse.ArgumentParser(description="BiScEF map plotter",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 epilog="NB: This script assumes that the file(s) contains data from one day (or less)")
parser.add_argument("-G", "--GPS", action="store_true", help="Include GPS in plots")
parser.add_argument("-R", "--GLONASS", action="store_true", help="Include GLONASS in plots")
parser.add_argument("-E", "--Galileo", action="store_true", help="Include Galileo in plots")
parser.add_argument("-C", "--BeiDou", action="store_true", help="Include BeiDou in plots")
parser.add_argument("-S", "--SBAS", action="store_true", help="Include SBAS in plots")
parser.add_argument("--sigmaPhi_1", action="store_true", help="Plot map(s) of sig1 sigma_phi")
parser.add_argument("--sigmaPhi_2", action="store_true", help="Plot map(s) of sig2 sigma_phi")
parser.add_argument("--S4_1", action="store_true", help="Plot map(s) of sig1 S4")
parser.add_argument("--S4_2", action="store_true", help="Plot map(s) of sig2 S4")
parser.add_argument("--CN0_1", action="store_true", help="Plot map(s) of sig1 C/N0")
parser.add_argument("--CN0_2", action="store_true", help="Plot map(s) of sig2 C/N0")
parser.add_argument("--ROTI", action="store_true", help="Plot map(s) of 1Hz ROTI")
parser.add_argument("--TEC", action="store_true", help="Plot map(s) of calibrated TEC")
parser.add_argument("--elevationCutoff", type=float, default=5, help="Set elevation angle cutoff")
parser.add_argument("--minutesPerPlot", type=int, default=5, help="Minutes of data per plot. If it is set to zero, make one plot containing all data.")
parser.add_argument("--outputPath", type=str, default="./", help="Folder in which to save output plot files")
parser.add_argument("--outputFilenameBase", type=str, default="Plot", help="Base of output file name (string at start of filename) (data type and time will be appended to it by the script)")
parser.add_argument("filename", nargs="+", help="Filename(s) of input data file(s)")
args = parser.parse_args()
config = vars(args)
# FOR DEBUGGING: print(config)
# FOR DEBUGGING: sys.exit("testing")


# Construct list of constellations to plot (and a string listing them)
constToPlot = []
constListStr = ""
b = False
if(config['GPS']):
	constToPlot.append('GPS')
	constListStr = constListStr + "GPS"
	b = True
if(config['GLONASS']):
	constToPlot.append('GLONASS')
	if b :
		constListStr = constListStr + ", "
	constListStr = constListStr + "GLONASS"
	b = True
if(config['Galileo']):
	constToPlot.append('Galileo')
	if b :
		constListStr = constListStr + ", "
	constListStr = constListStr + "Galileo"
	b = True
if(config['BeiDou']):
	constToPlot.append('BeiDou')
	if b :
		constListStr = constListStr + ", "
	constListStr = constListStr + "BeiDou"
	b = True
if(config['SBAS']):
	constToPlot.append('SBAS')
	if b :
		constListStr = constListStr + ", "
	constListStr = constListStr + "SBAS"
	b = True

# Boolean arrays for sorting/filtering
constFilter = dict()

# Data storage
dataTimes = dict()
dataValues = dict()
dataLons = dict()
dataLats = dict()
unitStr = dict()    # Note: The loading code gets the value for this whenever it finds it. In other words, it does not check that all files use the same unit. (they should)

# Datatypes to plot
datatypes = []
if(config['sigmaPhi_1']):
	init_data_storage('Phi60s1')
if(config['sigmaPhi_2']):
	init_data_storage('Phi60s2')
if(config['S4_1']):
	init_data_storage('S4s1')
if(config['S4_2']):
	init_data_storage('S4s2')
if(config['CN0_1']):
	init_data_storage('AvgCN0s1')
if(config['CN0_2']):
	init_data_storage('AvgCN0s2')
if(config['ROTI']):
	init_data_storage('ROTI1Hz')
if(config['TEC']):
	init_data_storage('TECtow')




# Loop to read files
for filename in config['filename']:
	print("\nNow reading " + filename)
	f = h5py.File(filename, 'r')
	if not f:
		print("Warning: Failed to open \"" + config['filename'] + "\"")
		continue
	# Construct boolean arrays for sorting/filtering	
	constFilter['GPS']     = (f['SVID'][()] >   0) & (f['SVID'][()] <  33)
	constFilter['GLONASS'] = (f['SVID'][()] >  37) & (f['SVID'][()] <  63)
	constFilter['Galileo'] = (f['SVID'][()] >  70) & (f['SVID'][()] < 107)
	constFilter['SBAS']    = ((f['SVID'][()] > 119) & (f['SVID'][()] < 141)) | ((f['SVID'][()] > 197) & (f['SVID'][()] < 216))
	constFilter['BeiDou']  = ((f['SVID'][()] > 140) & (f['SVID'][()] < 181)) | ((f['SVID'][()] > 222) & (f['SVID'][()] < 246))
	elevFilter = f['Elevation'][()] >= config['elevationCutoff']

	# Check if IPP map coords are present
	if not 'Latitude' in f.keys():
		print(" ERROR: No IPP Latitude information in file. Cannot plot these data on a map.")
		f.close()
		continue
	if not 'Longitude' in f.keys():
		print(" ERROR: No IPP Longitude information in file. Cannot plot these data on a map.")
		f.close()
		continue

	# Extract data we want into arrays
	for datatype in datatypes :
		if not datatype in f.keys():
			print(" No " + datatype + " data in " + filename)
			continue

		for const in constToPlot :
			extract_data(const, datatype)

		print("Total " + datatype + "data records: " + str(len(dataValues[datatype])))

	f.close()


# Loop over datatypes
for datatype in datatypes :
	# If no data, continue
	if len(dataValues[datatype]) == 0:
		continue

	# Make plot(s)
	if config['minutesPerPlot'] == 0: # Plot all loaded data in 1 plot
		startTime = min(dataTimes[datatype])
		endTime = max(dataTimes[datatype])
		timeStr = startTime.strftime("%Y-%m-%d")
		filenameStr = config['outputPath'] + "/" + config['outputFilenameBase'] + "_Map_" + plotParams[datatype]['fnamestr'] + startTime.strftime("_%Y%m%d")
		if(timeStr != endTime.strftime("%Y-%m-%d")):
			timeStr = timeStr + " to " + endTime.strftime("%Y-%m-%d")
			filenameStr = filenameStr + "to" + endTime.strftime("%Y%m%d")
		plot_map(datatype, dataValues[datatype], dataLons[datatype], dataLats[datatype], timeStr, filenameStr)
	else: # Make M-minute plots
		M = config['minutesPerPlot']
		startTime = min(dataTimes[datatype])
		startTime = startTime - timedelta(minutes=startTime.minute % M, seconds=startTime.second, microseconds=startTime.microsecond)
		endTime = max(dataTimes[datatype])
		delta = timedelta(minutes=M)
		while startTime <= endTime:
			timeStr = startTime.strftime("%Y-%m-%d %H:%M") + " to " + (startTime + delta).strftime("%H:%M")
			filenameStr = config['outputPath'] + "/" + config['outputFilenameBase'] + "_Map_" + plotParams[datatype]['fnamestr'] + startTime.strftime("_%Y%m%d_%H%M")
			r = [(x >= startTime) & (x < startTime + delta) for x in dataTimes[datatype]]
			plot_map(datatype, list(compress(dataValues[datatype], r)), list(compress(dataLons[datatype], r)), list(compress(dataLats[datatype], r)), timeStr, filenameStr)
			startTime += delta



