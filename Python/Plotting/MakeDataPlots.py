import os
import sys
import h5py    
import numpy as np   
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from itertools import compress

# NB: This script assumes that the file contains data from one day (or less)

# Input from command line: one filename
fname = str(sys.argv[1])
datapath = os.path.dirname(fname)
basename = os.path.basename(fname)
fnamestem = os.path.splitext(basename)[0]

# Open file
print("Now reading " + fname)
f = h5py.File(fname, 'r')
if not f:
	sys.exit("Failed to open \"" + fname + "\"")


# Get info
recCode = f.attrs['ReceiverCode']
dateStr = datetime.strftime(datetime.utcfromtimestamp(min(f['UNIXTime'])), "%Y-%m-%d")

# Convert UNIX time array to list of UTC datetimes
dt_utcdatetimes = [datetime.utcfromtimestamp(x) for x in f['UNIXTime'][()]]

# Construct boolean arrays for sorting/filtering
isGPS = (f['SVID'][()] > 0) & (f['SVID'][()] < 33)




# Make plot - Simple scatter plot time series

fig, axs = plt.subplots(2)
plotWasMade = False
if 'Phi60s1' in f.keys():
	if 'Unit' in f['Phi60s1'].attrs.keys():
		unitStr = f['Phi60s1'].attrs['Unit']
	else:
		unitStr = '?'
	axs[0].plot(list(compress(mdates.date2num(dt_utcdatetimes), isGPS)), list(compress(f['Phi60s1'][()], isGPS)), '.')
	axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
	axs[0].xaxis.set_major_locator(mdates.HourLocator())
	axs[0].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
	axs[0].set_ylim([0, 1])
	axs[0].set_ylabel(r'Sig1 $\sigma_\phi$ (' + unitStr + ')')
	axs[0].set_title('Phase Scintillation, ' + recCode + ', GPS, ' + dateStr)
	axs[0].grid()
	plotWasMade = True

if 'Phi60s2' in f.keys():
	if 'Unit' in f['Phi60s2'].attrs.keys():
		unitStr = f['Phi60s2'].attrs['Unit']
	else:
		unitStr = '?'
	axs[1].plot(list(compress(mdates.date2num(dt_utcdatetimes), isGPS)), list(compress(f['Phi60s2'][()], isGPS)), '.')
	axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
	axs[1].xaxis.set_major_locator(mdates.HourLocator())
	axs[1].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
	axs[1].set_ylim([0, 1])
	axs[1].set_xlabel('UTC hour-of-day')
	axs[1].set_ylabel(r'Sig2 $\sigma_\phi$ (' + unitStr + ')')
	axs[1].grid()
	plotWasMade = True

if plotWasMade:
	plt.savefig(datapath + '/' + fnamestem + '_PhaseScint' + '.png', dpi=300)




# Make plot - Box-and-whiskers time series

hours = range(0, 24)
fig, axs = plt.subplots(2)

if 'Phi60s1' in f.keys():
	hasValue = f['Phi60s1'][()] > 0
	dHourlyPhi60s1 = []
	for hour in hours:
		tr = [x.hour == hour for x in dt_utcdatetimes]
		dHourlyPhi60s1.append(list(compress(f['Phi60s1'][()], isGPS & tr & hasValue)))
	if 'Unit' in f['Phi60s1'].attrs.keys():
		unitStr = f['Phi60s1'].attrs['Unit']
	else:
		unitStr = '?'
	axs[0].boxplot(dHourlyPhi60s1, positions=hours)
	axs[0].set_ylim([0, 1])
	axs[0].set_ylabel(r'Sig1 $\sigma_\phi$ (' + unitStr + ')')
	axs[0].set_title('Phase Scintillation, ' + recCode + ', GPS, ' + dateStr)
	axs[0].grid()


if 'Phi60s2' in f.keys():
	hasValue = f['Phi60s2'][()] > 0
	dHourlyPhi60s2 = []
	for hour in hours:
		tr = [x.hour == hour for x in dt_utcdatetimes]
		dHourlyPhi60s2.append(list(compress(f['Phi60s2'][()], isGPS & tr & hasValue)))
	if 'Unit' in f['Phi60s2'].attrs.keys():
		unitStr = f['Phi60s2'].attrs['Unit']
	else:
		unitStr = '?'
	axs[1].boxplot(dHourlyPhi60s2, positions=hours)
	axs[1].set_ylim([0, 1])
	axs[1].set_ylabel(r'Sig2 $\sigma_\phi$ (' + unitStr + ')')
	axs[1].set_xlabel('UTC hour-of-day')
	axs[1].grid()


plt.savefig(datapath + '/' + fnamestem + '_PhaseScintBoxPlot' + '.png', dpi=300)



# Make plot - Skyplot (TODO)
#'Azimuth', 'Elevation'



# Make plot - Dots on map (TODO)
# 'Longitude', 'Latitude'


# TODO - Other constellations

# TODO - CN0 plots
# 'AvgCN0s1', 'AvgCN0s2', 'AvgCN0s3'

# TODO - S4 plots
#'S4s1', 'S4s2', 'S4s3', 

# TODO - Spectral parameters plots
#'Ts1', 'Ts2', 'Ts3', 
#'phighs1', 'plows1', 'pmids1', 'ps1', 'ps2', 'ps3'

# TODO - TEC plots
# 'TECtow'
# 'TECtow_uncal'

# TODO - ROTI plots
#'ROTI1Hz', 'ROTIFullHz', 





