import os
import sys
import h5py    
import numpy as np 
import pandas as pd  
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.dates as mdates
from datetime import datetime
from itertools import compress

# NB: This script assumes that the file contains data from one day (or less)


# Plotting parameters defined per data type
plotParams = { 'Phi60s1':      {'lim': [0, 1], 'label': r'Sig1 $\sigma_\phi$', 'hasunit': True,  'canbenegative': False, 'title': 'Phase Scintillation', 'fnamestr': 'PhaseScint'},
               'Phi60s2':      {'lim': [0, 1], 'label': r'Sig2 $\sigma_\phi$', 'hasunit': True,  'canbenegative': False, 'title': 'Phase Scintillation'},
               'S4s1':         {'lim': [0, 1], 'label': 'Sig1 S4',             'hasunit': False, 'canbenegative': False, 'title': 'Amplitude Scintillation', 'fnamestr': 'AmpScint'},
               'S4s2':         {'lim': [0, 1], 'label': 'Sig2 S4',             'hasunit': False, 'canbenegative': False, 'title': 'Amplitude Scintillation'},
               'AvgCN0s1':     {               'label': 'Sig1 C/N0',           'hasunit': True,  'canbenegative': False, 'title': 'Carrier/Noise ratio', 'fnamestr': 'CN0'},
               'AvgCN0s2':     {               'label': 'Sig2 C/N0',           'hasunit': True,  'canbenegative': False, 'title': 'Carrier/Noise ratio'},
               'Ts1':          {               'label': 'Sig1 T',              'hasunit': True,  'canbenegative': False, 'title': 'Phase power spectral density at 1 Hz', 'fnamestr': 'PSDT1Hz'},
               'Ts2':          {               'label': 'Sig2 T',              'hasunit': True,  'canbenegative': False, 'title': 'Phase power spectral density at 1 Hz'},
               'phighs1':      {               'label': 'Sig1 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope', 'legend': '(16 to 25 Hz)', 'fnamestr': 'PSDSlopeParts'},
               'plows1':       {               'label': 'Sig1 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope', 'legend': '(0.1 to 8 Hz)'},
               'pmids1':       {               'label': 'Sig1 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope', 'legend': '(8 to 16 Hz)'},
               'ps1':          {               'label': 'Sig1 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope (0.1 to 25 Hz)', 'fnamestr': 'PSDSlope'},
               'ps2':          {               'label': 'Sig2 slope',          'hasunit': False, 'canbenegative': True,  'title': 'Spectral slope (0.1 to 25 Hz)'},
               'TECtow':       {               'label': 'TEC',                 'hasunit': True,  'canbenegative': False, 'title': 'TEC', 'fnamestr': 'TEC'},
               'TECtow_uncal': {               'label': 'TEC',                 'hasunit': True,  'canbenegative': True,  'title': 'TEC (uncalibrated)', 'fnamestr': 'uTEC'},
               'ROTI1Hz':      {'lim': [0, 10], 'label': r'ROTI$_{1Hz}$',      'hasunit': True,  'canbenegative': False, 'title': 'ROTI', 'fnamestr': 'ROTI'},
               'ROTIFullHz':   {               'label': r'ROTI$_{FullHz}$',    'hasunit': True,  'canbenegative': False, 'title': 'ROTI from full-resolution data', 'fnamestr': 'ROTIf'},
             }
	# (Note: if 'lim' is not defined, plot will auto-scale)


def plot_timeseries_simple(constFilter, constStr, datatypes):

	if len(datatypes) == 0:
		return

	fig, axs = plt.subplots(len(datatypes))
	plotWasMade = False
	if(len(datatypes) == 1):
		axs = [axs]; # The code below assumes that 'axs' is a list, but subplots() does not return a list if only one panel is requested.
	
	panelI = 0
	for datatype in datatypes:
		if datatype in f.keys():
			if plotParams[datatype]['canbenegative']:
				hasValue = (f[datatype][()] != 0) & (f[datatype][()] == f[datatype][()])
			else:
				hasValue = (f[datatype][()] > 0) & (f[datatype][()] == f[datatype][()])
			totalFilter = constFilter & hasValue & elevFilter
			if sum(totalFilter) > 0:
				if 'Unit' in f[datatype].attrs.keys():
					unitStr = f[datatype].attrs['Unit']
				else:
					unitStr = '?'
				if 'legend' in plotParams[datatype]:
					axs[panelI].plot(list(compress(mdates.date2num(dt_utcdatetimes), totalFilter)), list(compress(f[datatype][()], totalFilter)), '.', label = plotParams[datatype]['legend'])
					axs[panelI].legend(loc='upper right')
				else:
					axs[panelI].plot(list(compress(mdates.date2num(dt_utcdatetimes), totalFilter)), list(compress(f[datatype][()], totalFilter)), '.')
				axs[panelI].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
				axs[panelI].xaxis.set_major_locator(mdates.HourLocator())
				axs[panelI].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
				if 'lim' in plotParams[datatype]:
					axs[panelI].set_ylim(plotParams[datatype]['lim'])
				if plotParams[datatype]['hasunit']:
					axs[panelI].set_ylabel(plotParams[datatype]['label'] + ' (' + unitStr + ')')
				else:
					axs[panelI].set_ylabel(plotParams[datatype]['label'])
				if panelI == 0:
					axs[panelI].set_title(plotParams[datatype]['title'] + ', ' + recCode + ', ' + constStr + ', ' + dateStr)
				if panelI == len(datatypes)-1:
					axs[panelI].set_xlabel('UTC hour-of-day')
				axs[panelI].grid()
				plotWasMade = True
		panelI = panelI + 1

	if plotWasMade:
		plotfname = datapath + '/' + fnamestem + '_' + plotParams[datatypes[0]]['fnamestr'] + '_' + constStr + '.png'
		plt.savefig(plotfname, dpi=300)
		print("Saved plot to " + plotfname)


def plot_timeseries_box(constFilter, constStr, datatypes):
	if len(datatypes) == 0:
		return

	fig, axs = plt.subplots(len(datatypes))
	plotWasMade = False
	if(len(datatypes) == 1):
		axs = [axs]; # The code below assumes that 'axs' is a list, but subplots() does not return a list if only one panel is requested.
	
	hours = range(0, 24)

	panelI = 0
	for datatype in datatypes:
		if datatype in f.keys():
			if plotParams[datatype]['canbenegative']:
				hasValue = (f[datatype][()] != 0) & (f[datatype][()] == f[datatype][()])
			else:
				hasValue = (f[datatype][()] > 0) & (f[datatype][()] == f[datatype][()])
			totalFilter = constFilter & hasValue & elevFilter
			if sum(totalFilter) > 0:
				if 'Unit' in f[datatype].attrs.keys():
					unitStr = f[datatype].attrs['Unit']
				else:
					unitStr = '?'
				dHourlyData = []
				for hour in hours:
					tr = [x.hour == hour for x in dt_utcdatetimes]
					dHourlyData.append(list(compress(f[datatype][()], totalFilter & tr)))
				bp = axs[panelI].boxplot(dHourlyData, positions = hours)
				if 'legend' in plotParams[datatype]:
					axs[panelI].legend([bp["boxes"][0]], [plotParams[datatype]['legend']], loc='upper right')
				if 'lim' in plotParams[datatype]:
					axs[panelI].set_ylim(plotParams[datatype]['lim'])
				if plotParams[datatype]['hasunit']:
					axs[panelI].set_ylabel(plotParams[datatype]['label'] + ' (' + unitStr + ')')
				else:
					axs[panelI].set_ylabel(plotParams[datatype]['label'])
				if panelI == 0:
					axs[panelI].set_title(plotParams[datatype]['title'] + ', ' + recCode + ', ' + constStr + ', ' + dateStr)
				if panelI == len(datatypes)-1:
					axs[panelI].set_xlabel('UTC hour-of-day')
				axs[panelI].grid()
				plotWasMade = True
		panelI = panelI + 1

	if plotWasMade:
		plotfname = datapath + '/' + fnamestem + '_BoxPlot_' + plotParams[datatypes[0]]['fnamestr'] + '_' + constStr + '.png'
		plt.savefig(plotfname, dpi=300)
		print("Saved plot to " + plotfname)


def plot_sky(constFilter, constStr, datatype, sizescale = 1):
	if datatype in f.keys():
		if plotParams[datatype]['canbenegative']:
			hasValue = (f[datatype][()] != 0) & (f[datatype][()] == f[datatype][()])
		else:
			hasValue = (f[datatype][()] > 0) & (f[datatype][()] == f[datatype][()])

		totalFilter = constFilter & hasValue & elevFilter
		if sum(totalFilter) == 0:
			return

		if 'Unit' in f[datatype].attrs.keys():
			unitStr = f[datatype].attrs['Unit']
		else:
			unitStr = '?'

		theta = list(compress(f['Azimuth'][()] * np.pi / 180, totalFilter))
		r = list(compress(90 - f['Elevation'][()], totalFilter))
		colors = list(compress(f[datatype][()], totalFilter))
		area = list(compress(1 + f[datatype][()] * 30 * sizescale, totalFilter))

		fig = plt.figure()
		ax = fig.add_subplot(projection='polar')
		ax.set_theta_zero_location("N")
		im = ax.scatter(theta, r, c=colors, s=area, cmap=plt.cm.jet, alpha=0.75)
		if 'lim' in plotParams[datatype]:
			im.set_clim(plotParams[datatype]['lim'])
		ax.set_rlim([0, 90])
		ax.set_yticks(range(0, 91, 30))
		ax.set_yticklabels(['90$^{\circ}$', '60$^{\circ}$', '30$^{\circ}$', '0$^{\circ}$'])
		ax.set_title(datatype + ', ' + recCode + ', ' + constStr + ', ' + dateStr)
		cb = fig.colorbar(im, ax=ax)
		if plotParams[datatype]['hasunit']:
			cb.set_label(plotParams[datatype]['label'] + ' (' + unitStr + ')')
		else:
			cb.set_label(plotParams[datatype]['label'])

		plotfname = datapath + '/' + fnamestem + '_SkyPlot_' + plotParams[datatype]['fnamestr'] + '_' + constStr + '.png'
		plt.savefig(plotfname, dpi=300)
		print("Saved plot to " + plotfname)


def plot_heat_sigPhi(constFilter, constStr):
	fig, axs = plt.subplots(2)
	plotWasMade = False
	
	if 'Phi60s1' in f.keys():
		hasValue = f['Phi60s1'][()] > 0
		totalFilter = constFilter & hasValue & elevFilter
		if sum(totalFilter) > 0:
			if 'Unit' in f['Phi60s1'].attrs.keys():
				unitStr = f['Phi60s1'].attrs['Unit']
			else:
				unitStr = '?'
			
			UNIX = list(compress(f['UNIXTime'][()], totalFilter))
			uniqTime = np.unique(UNIX)
			utcTime = list((compress(mdates.date2num(dt_utcdatetimes), totalFilter)))
			df = pd.DataFrame()
			df['Phi'] = list(compress(f['Phi60s1'][()], totalFilter))
			df['unixtime'] = list(compress(f['UNIXTime'][()], totalFilter))
			Phi60s1Mean = []
			for t in uniqTime:
				Phitemp = df.loc[df.unixtime == t]
				Phi60s1Mean.append(Phitemp.Phi.mean())
				
			Phibins = np.linspace(0, 1, 50)
			timebins = np.linspace(utcTime[0], utcTime[-1], 288)
			
			axs[0].plot(np.unique(list((compress(mdates.date2num(dt_utcdatetimes), totalFilter)))), Phi60s1Mean, 'r', linewidth=0.5)
			axs[0].hist2d(utcTime, df.Phi.astype(float), bins=[timebins,Phibins], norm = colors.LogNorm())
			axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
			axs[0].xaxis.set_major_locator(mdates.HourLocator())
			axs[0].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
			axs[0].set_ylim([0, 1])
			axs[0].set_ylabel(r'Sig1 $\sigma_\phi$ (' + unitStr + ')')
			axs[0].set_title('Mean of Phase Scintillation, ' + recCode + ', ' + constStr + ', ' + dateStr)
			axs[0].grid()
			plotWasMade = True
			
	if 'Phi60s2' in f.keys():
		hasValue = f['Phi60s2'][()] > 0
		totalFilter = constFilter & hasValue & elevFilter
		if sum(totalFilter) > 0:
			if 'Unit' in f['Phi60s2'].attrs.keys():
				unitStr = f['Phi60s2'].attrs['Unit']
			else:
				unitStr = '?'
			
			UNIX = list(compress(f['UNIXTime'][()], totalFilter))
			uniqTime = np.unique(UNIX)
			utcTime = list((compress(mdates.date2num(dt_utcdatetimes), totalFilter)))
			df = pd.DataFrame()
			df['Phi'] = list(compress(f['Phi60s2'][()], totalFilter))
			df['unixtime'] = list(compress(f['UNIXTime'][()], totalFilter))
			Phi60s2Mean = []
			for t in uniqTime:
				Phitemp = df.loc[df.unixtime == t]
				Phi60s2Mean.append(Phitemp.Phi.mean())
			
			Phibins = np.linspace(0, 1, 50)
			timebins = np.linspace(utcTime[0], utcTime[-1], 288)
			
			axs[1].plot(np.unique(list((compress(mdates.date2num(dt_utcdatetimes), totalFilter)))), Phi60s2Mean, 'r', linewidth=0.5)
			axs[1].hist2d(utcTime, df.Phi.astype(float), bins=[timebins,Phibins], norm = colors.LogNorm())
			axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
			axs[1].xaxis.set_major_locator(mdates.HourLocator())
			axs[1].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
			axs[1].set_ylim([0, 1])
			axs[1].set_ylabel(r'Sig2 $\sigma_\phi$ (' + unitStr + ')')
			axs[1].set_xlabel('UTC hour-of-day')
			axs[1].grid()
			plotWasMade = True
			
	if plotWasMade:
		plotfname = datapath + '/' + fnamestem + '_PhaseScintHeatMap' + '_' + constStr + '.png'
		plt.savefig(plotfname, dpi=300)
		print("Saved plot to " + plotfname)


# Input from command line:
import argparse
parser = argparse.ArgumentParser(description="BiScEF data plotter",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 epilog="NB: This script assumes that the file contains data from one day (or less)")
parser.add_argument("-G", "--GPS", action="store_true", help="Make plots for GPS")
parser.add_argument("-R", "--GLONASS", action="store_true", help="Make plots for GLONASS")
parser.add_argument("-E", "--Galileo", action="store_true", help="Make plots for Galileo")
parser.add_argument("-C", "--BeiDou", action="store_true", help="Make plots for BeiDou")
parser.add_argument("-S", "--SBAS", action="store_true", help="Make plots for SBAS")
parser.add_argument("--plot_ts_simple", action="store_true", help="Plot simple time series")
parser.add_argument("--plot_ts_box", action="store_true", help="Plot box-and-whiskers time series")
parser.add_argument("--plot_sky", action="store_true", help="Plot skyplots")
parser.add_argument("--plot_heat_sigPhi", action="store_true", help="Plot 2d histogram of sigma phi over time with mean sigma phi")
parser.add_argument("--elevationCutoff", type=float, default=5, help="Set elevation angle cutoff")
parser.add_argument("filename", help="Filename of input data file")
args = parser.parse_args()
config = vars(args)
# FOR DEBUGGING: print(config)
# FOR DEBUGGING: sys.exit("testing")

# Derived from command line input
datapath = os.path.dirname(config['filename'])
basename = os.path.basename(config['filename'])
fnamestem = os.path.splitext(basename)[0]

# Open file
print("Now reading " + config['filename'])
f = h5py.File(config['filename'], 'r')
if not f:
	sys.exit("Failed to open \"" + config['filename'] + "\"")

# Get info
recCode = f.attrs['ReceiverCode']
dateStr = datetime.strftime(datetime.utcfromtimestamp(min(f['UNIXTime'])), "%Y-%m-%d")

# Convert UNIX time array to list of UTC datetimes
dt_utcdatetimes = [datetime.utcfromtimestamp(x) for x in f['UNIXTime'][()]]

# Construct boolean arrays for sorting/filtering
constFilter = dict()
constFilter['GPS']     = (f['SVID'][()] >   0) & (f['SVID'][()] <  33)
constFilter['GLONASS'] = (f['SVID'][()] >  37) & (f['SVID'][()] <  63)
constFilter['Galileo'] = (f['SVID'][()] >  70) & (f['SVID'][()] < 107)
constFilter['SBAS']    = ((f['SVID'][()] > 119) & (f['SVID'][()] < 141)) | ((f['SVID'][()] > 197) & (f['SVID'][()] < 216))
constFilter['BeiDou']  = ((f['SVID'][()] > 140) & (f['SVID'][()] < 181)) | ((f['SVID'][()] > 222) & (f['SVID'][()] < 246))
elevFilter = f['Elevation'][()] >= config['elevationCutoff']

# Construct list of constellations to plot
constToPlot = []
if(config['GPS']):
	constToPlot.append('GPS')
if(config['GLONASS']):
	constToPlot.append('GLONASS')
if(config['Galileo']):
	constToPlot.append('Galileo')
if(config['BeiDou']):
	constToPlot.append('BeiDou')
if(config['SBAS']):
	constToPlot.append('SBAS')


# Make plot - Simple scatter plot time series
if(config['plot_ts_simple']):
	for const in constToPlot:
		plot_timeseries_simple(constFilter[const], const, ['Phi60s1', 'Phi60s2'])
		plot_timeseries_simple(constFilter[const], const, ['S4s1', 'S4s2'])
		plot_timeseries_simple(constFilter[const], const, ['AvgCN0s1', 'AvgCN0s2'])
		plot_timeseries_simple(constFilter[const], const, ['Ts1', 'Ts2'])
		plot_timeseries_simple(constFilter[const], const, ['ps1', 'ps2'])
		plot_timeseries_simple(constFilter[const], const, ['phighs1', 'pmids1', 'plows1'])
		plot_timeseries_simple(constFilter[const], const, ['TECtow'])
		plot_timeseries_simple(constFilter[const], const, ['TECtow_uncal'])
		plot_timeseries_simple(constFilter[const], const, ['ROTI1Hz'])

# Make plot - Box-and-whiskers time series
if(config['plot_ts_box']):
	for const in constToPlot:
		plot_timeseries_box(constFilter[const], const, ['Phi60s1', 'Phi60s2'])
		plot_timeseries_box(constFilter[const], const, ['S4s1', 'S4s2'])
		plot_timeseries_box(constFilter[const], const, ['AvgCN0s1', 'AvgCN0s2'])
		plot_timeseries_box(constFilter[const], const, ['Ts1', 'Ts2'])
		plot_timeseries_box(constFilter[const], const, ['ps1', 'ps2'])
		plot_timeseries_box(constFilter[const], const, ['phighs1', 'pmids1', 'plows1'])
		plot_timeseries_box(constFilter[const], const, ['TECtow'])
		plot_timeseries_box(constFilter[const], const, ['ROTI1Hz'])

# Make plot - Skyplot
if(config['plot_sky']):
	for const in constToPlot:
		plot_sky(constFilter[const], const, 'Phi60s1')
		plot_sky(constFilter[const], const, 'S4s1')
		plot_sky(constFilter[const], const, 'AvgCN0s1', 1.0 / 40)
		plot_sky(constFilter[const], const, 'ROTI1Hz', 1.0 / 10)

# Make plot - Heat map of sigma phi + time series of its mean
if(config['plot_heat_sigPhi']):
	for const in constToPlot:
		plot_heat_sigPhi(constFilter[const], const)

# Make plot - Dots on map (TODO)
# 'Longitude', 'Latitude'





