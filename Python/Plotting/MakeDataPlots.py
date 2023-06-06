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

def plot_timeseries_simple(constFilter, constStr):
	fig, axs = plt.subplots(2)
	plotWasMade = False

	if 'Phi60s1' in f.keys():
		hasValue = f['Phi60s1'][()] > 0
		if sum(constFilter & hasValue) > 0:
			if 'Unit' in f['Phi60s1'].attrs.keys():
				unitStr = f['Phi60s1'].attrs['Unit']
			else:
				unitStr = '?'
			axs[0].plot(list(compress(mdates.date2num(dt_utcdatetimes), constFilter & hasValue)), list(compress(f['Phi60s1'][()], constFilter & hasValue)), '.')
			axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
			axs[0].xaxis.set_major_locator(mdates.HourLocator())
			axs[0].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
			axs[0].set_ylim([0, 1])
			axs[0].set_ylabel(r'Sig1 $\sigma_\phi$ (' + unitStr + ')')
			axs[0].set_title('Phase Scintillation, ' + recCode + ', ' + constStr + ', ' + dateStr)
			axs[0].grid()
			plotWasMade = True

	if 'Phi60s2' in f.keys():
		hasValue = f['Phi60s2'][()] > 0
		if sum(constFilter & hasValue) > 0:
			if 'Unit' in f['Phi60s2'].attrs.keys():
				unitStr = f['Phi60s2'].attrs['Unit']
			else:
				unitStr = '?'
			axs[1].plot(list(compress(mdates.date2num(dt_utcdatetimes), constFilter & hasValue)), list(compress(f['Phi60s2'][()], constFilter & hasValue)), '.')
			axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
			axs[1].xaxis.set_major_locator(mdates.HourLocator())
			axs[1].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
			axs[1].set_ylim([0, 1])
			axs[1].set_xlabel('UTC hour-of-day')
			axs[1].set_ylabel(r'Sig2 $\sigma_\phi$ (' + unitStr + ')')
			axs[1].grid()
			plotWasMade = True

	if plotWasMade:
		plotfname = datapath + '/' + fnamestem + '_PhaseScint' + '_' + constStr + '.png'
		plt.savefig(plotfname, dpi=300)
		print("Saved plot to " + plotfname)


def plot_timeseries_box(constFilter, constStr):
	hours = range(0, 24)
	fig, axs = plt.subplots(2)
	plotWasMade = False
	if 'Phi60s1' in f.keys():
		hasValue = f['Phi60s1'][()] > 0
		if sum(constFilter & hasValue) > 0:
			dHourlyPhi60s1 = []
			for hour in hours:
				tr = [x.hour == hour for x in dt_utcdatetimes]
				dHourlyPhi60s1.append(list(compress(f['Phi60s1'][()], constFilter & tr & hasValue)))
			if 'Unit' in f['Phi60s1'].attrs.keys():
				unitStr = f['Phi60s1'].attrs['Unit']
			else:
				unitStr = '?'
			axs[0].boxplot(dHourlyPhi60s1, positions=hours)
			axs[0].set_ylim([0, 1])
			axs[0].set_ylabel(r'Sig1 $\sigma_\phi$ (' + unitStr + ')')
			axs[0].set_title('Phase Scintillation, ' + recCode + ', ' + constStr + ', ' + dateStr)
			axs[0].grid()
			plotWasMade = True

	if 'Phi60s2' in f.keys():
		hasValue = f['Phi60s2'][()] > 0
		if sum(constFilter & hasValue) > 0:
			dHourlyPhi60s2 = []
			for hour in hours:
				tr = [x.hour == hour for x in dt_utcdatetimes]
				dHourlyPhi60s2.append(list(compress(f['Phi60s2'][()], constFilter & tr & hasValue)))
			if 'Unit' in f['Phi60s2'].attrs.keys():
				unitStr = f['Phi60s2'].attrs['Unit']
			else:
				unitStr = '?'
			axs[1].boxplot(dHourlyPhi60s2, positions=hours)
			axs[1].set_ylim([0, 1])
			axs[1].set_ylabel(r'Sig2 $\sigma_\phi$ (' + unitStr + ')')
			axs[1].set_xlabel('UTC hour-of-day')
			axs[1].grid()
			plotWasMade = True

	if plotWasMade:
		plotfname = datapath + '/' + fnamestem + '_PhaseScintBoxPlot' + '_' + constStr + '.png'
		plt.savefig(plotfname, dpi=300)
		print("Saved plot to " + plotfname)


def plot_sky_sigPhi(constFilter, constStr, sigNum):
	datatype = 'Phi60s' + str(sigNum)
	if datatype in f.keys():
		hasValue = f[datatype][()] > 0

		if sum(constFilter & hasValue) == 0:
			return

		if 'Unit' in f[datatype].attrs.keys():
			unitStr = f[datatype].attrs['Unit']
		else:
			unitStr = '?'

		theta = list(compress(f['Azimuth'][()] * np.pi / 180, constFilter & hasValue))
		r = list(compress(90 - f['Elevation'][()], constFilter & hasValue))
		colors = list(compress(f[datatype][()], constFilter & hasValue))
		area = list(compress(1 + f[datatype][()] * 30, constFilter & hasValue))

		fig = plt.figure()
		ax = fig.add_subplot(projection='polar')
		ax.set_theta_zero_location("N")
		im = ax.scatter(theta, r, c=colors, s=area, cmap=plt.cm.jet, alpha=0.75)
		im.set_clim([0, 1])
		ax.set_rlim([0, 90])
		ax.set_yticks(range(0, 91, 30))
		ax.set_yticklabels(['90$^{\circ}$', '60$^{\circ}$', '30$^{\circ}$', '0$^{\circ}$'])
		ax.set_title(datatype + ', ' + recCode + ', ' + constStr + ', ' + dateStr)
		cb = fig.colorbar(im, ax=ax)
		cb.set_label(r'Sig' + str(sigNum) + ' $\sigma_\phi$ (' + unitStr + ')')

		plotfname = datapath + '/' + fnamestem + '_' + 'Phi60s' + str(sigNum) + '_' + 'SkyPlot' + '_' + constStr + '.png'
		plt.savefig(plotfname, dpi=300)
		print("Saved plot to " + plotfname)

def plot_PhiMean2dHist(constFilter, constStr):
    fig, axs = plt.subplots(2)
    plotWasMade = False
    
    if 'Phi60s1' in f.keys():
        hasValue = f['Phi60s1'][()] > 0
        if sum(constFilter & hasValue) > 0:
            if 'Unit' in f['Phi60s1'].attrs.keys():
                unitStr = f['Phi60s1'].attrs['Unit']
            else:
                unitStr = '?'
            
            UNIX = list(compress(f['UNIXTime'][()], constFilter & hasValue))
            uniqTime = np.unique(UNIX)
            df = pd.DataFrame()
            df['Phi'] = list(compress(f['Phi60s1'][()], constFilter & hasValue))
            df['unixtime'] = list(compress(f['UNIXTime'][()], constFilter & hasValue))
            Phi60s1Mean = []
            for t in uniqTime:
                Phitemp = df.loc[df.unixtime == t]
                Phi60s1Mean.append(Phitemp.Phi.mean())
                
            Phibins = np.linspace(0, 1, 50)
            timebins = np.linspace(df.time.values[0], df.time.values[-1], 288)
            
            axs[0].plot(np.unique(list((compress(mdates.date2num(dt_utcdatetimes), constFilter & hasValue)))), Phi60s1Mean, 'k',linewidth=0.5)
            axs[0].hist2d(df.unixtime.astype(float),df.Phi.astype(float),bins=[timebins,Phibins],norm = colors.LogNorm())
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
        if sum(constFilter & hasValue) > 0:
            if 'Unit' in f['Phi60s2'].attrs.keys():
                unitStr = f['Phi60s2'].attrs['Unit']
            else:
                unitStr = '?'
            
            UNIX = list(compress(f['UNIXTime'][()], constFilter & hasValue))
            uniqTime = np.unique(UNIX)
            df = pd.DataFrame()
            df['Phi'] = list(compress(f['Phi60s2'][()], constFilter & hasValue))
            df['unixtime'] = list(compress(f['UNIXTime'][()], constFilter & hasValue))
            Phi60s2Mean = []
            for t in uniqTime:
                Phitemp = df.loc[df.unixtime == t]
                Phi60s2Mean.append(Phitemp.Phi.mean())
            
            Phibins = np.linspace(0, 1, 50)
            timebins = np.linspace(df.time.values[0], df.time.values[-1], 288)
            
            axs[1].plot(np.unique(list((compress(mdates.date2num(dt_utcdatetimes), constFilter & hasValue)))), Phi60s2Mean, 'k',linewidth=0.5)
            axs[1].hist2d(df.unixtime.astype(float),df.Phi.astype(float),bins=[timebins,Phibins],norm = colors.LogNorm())
            axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
            axs[1].xaxis.set_major_locator(mdates.HourLocator())
            axs[1].set_xlim([min(mdates.date2num(dt_utcdatetimes)), max(mdates.date2num(dt_utcdatetimes))])
            axs[1].set_ylim([0, 1])
            axs[1].set_ylabel(r'Sig1 $\sigma_\phi$ (' + unitStr + ')')
            axs[1].set_title('Mean of Phase Scintillation, ' + recCode + ', ' + constStr + ', ' + dateStr)
            axs[1].grid()
            plotWasMade = True
            
    if plotWasMade:
        plotfname = datapath + '/' + fnamestem + '_PhaseScintBoxPlot' + '_' + constStr + '.png'
        plt.savefig(plotfname, dpi=300)
        print("Saved plot to " + plotfname)
# Input from command line:
import argparse
parser = argparse.ArgumentParser(description="BiScEF data plotter",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 epilog="NB: This script assumes that the file contains data from one day (or less)")
parser.add_argument("--GPS", action="store_true", help="Make plots for GPS")
parser.add_argument("--GLONASS", action="store_true", help="Make plots for GLONASS")
parser.add_argument("--Galileo", action="store_true", help="Make plots for Galileo")
parser.add_argument("--BeiDou", action="store_true", help="Make plots for BeiDou")
parser.add_argument("--SBAS", action="store_true", help="Make plots for SBAS")
parser.add_argument("--plot_ts_simple", action="store_true", help="Plot simple time series of scintillation indices as simple time series")
parser.add_argument("--plot_ts_box", action="store_true", help="Plot box-and-whiskers time series of scintillation indices")
parser.add_argument("--plot_sky_sigPhi", action="store_true", help="Plot skyplots of phase scintillation indices")
parser.add_argument("--plot_PhiMean2dHist", action="store_true", help="Plot 2d histogram of sigma phi over time with mean sigma phi")
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
isGPS     = (f['SVID'][()] >   0) & (f['SVID'][()] <  33)
isGLONASS = (f['SVID'][()] >  37) & (f['SVID'][()] <  63)
isGalileo = (f['SVID'][()] >  70) & (f['SVID'][()] < 107)
isSBAS    = ((f['SVID'][()] > 119) & (f['SVID'][()] < 141)) | ((f['SVID'][()] > 197) & (f['SVID'][()] < 216))
isBeiDou  = ((f['SVID'][()] > 140) & (f['SVID'][()] < 181)) | ((f['SVID'][()] > 222) & (f['SVID'][()] < 246))


# Make plot - Simple scatter plot time series
if(config['plot_ts_simple']):
	if(config['GPS']):
		plot_timeseries_simple(isGPS, "GPS")
	if(config['GLONASS']):
		plot_timeseries_simple(isGLONASS, "GLONASS")
	if(config['Galileo']):
		plot_timeseries_simple(isGalileo, "Galileo")
	if(config['BeiDou']):
		plot_timeseries_simple(isBeiDou, "BeiDou")
	if(config['SBAS']):
		plot_timeseries_simple(isSBAS, "SBAS")


# Make plot - Box-and-whiskers time series
if(config['plot_ts_box']):
	if(config['GPS']):
		plot_timeseries_box(isGPS, "GPS")
	if(config['GLONASS']):
		plot_timeseries_box(isGLONASS, "GLONASS")
	if(config['Galileo']):
		plot_timeseries_box(isGalileo, "Galileo")
	if(config['BeiDou']):
		plot_timeseries_box(isBeiDou, "BeiDou")
	if(config['SBAS']):
		plot_timeseries_box(isSBAS, "SBAS")


# Make plot - Skyplot

if(config['plot_sky_sigPhi']):
	if(config['GPS']):
		plot_sky_sigPhi(isGPS, "GPS", 1)
	if(config['GLONASS']):
		plot_sky_sigPhi(isGLONASS, "GLONASS", 1)
	if(config['Galileo']):
		plot_sky_sigPhi(isGalileo, "Galileo", 1)
	if(config['BeiDou']):
		plot_sky_sigPhi(isBeiDou, "BeiDou", 1)
	if(config['SBAS']):
		plot_sky_sigPhi(isSBAS, "SBAS", 1)


# Make plot - PhiMean2dHist

if(config['plot_PhiMean2dHist']):
	if(config['GPS']):
		plot_PhiMean2dHist(isGPS, "GPS", 1)
	if(config['GLONASS']):
		plot_PhiMean2dHist(isGLONASS, "GLONASS", 1)
	if(config['Galileo']):
		plot_PhiMean2dHist(isGalileo, "Galileo", 1)
	if(config['BeiDou']):
		plot_PhiMean2dHist(isBeiDou, "BeiDou", 1)
	if(config['SBAS']):
		plot_PhiMean2dHist(isSBAS, "SBAS", 1)

# Make plot - Dots on map (TODO)
# 'Longitude', 'Latitude'


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





