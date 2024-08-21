# -*- coding: utf-8 -*-
"""
Created on Tue May  3 20:16:54 2022

@author: saschu
"""

import pandas as pd
import numpy as np
import os
from os.path import exists
import sys
import shutil
sys.path.append('') #Insert path to ISMR package
dataworkspace_path = ''#Insert path to workspace with data containing data
datalib_path = '' #Insert path to libary of datafiles



from ISMR import timeISMR

def load(doy:list,yr:str,stat:list):
    
    hr = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x"]
    mn = ["00","15","30","45"]
    varnames = ['GPSweek','TOW','sv','Rxstate','Azimuth','Elevation',
                'AvgCN0s1','S4s1','S4cors1','Phi01s1','Phi03s1','Phi10s1',
                'Phi30s1','Phi60s1','AvgCCDs1','SigmaCCDs1','TEC45','dTEC6045',
                'TEC30','dTEC4530','TEC15','dTEC3015','TECtow','dTEC15tow',
                'lockts1','sbfver','locktTEC','CN0TEC','SIs1','SInums1','ps1',
                'AvgCN0s2','S4s2','S4cors2','Phi01s2','Phi03s2','Phi10s2',
                'Phi30s2','Phi60s2','AvgCCDs2','SigmaCCDs2','lockts2','SIs2',
                'SInums2','ps2','AvgCN0s3','S4s3','S4cors3','Phi01s3',
                'Phi03s3','Phi10s3','Phi30s3','Phi60s3','AvgCCDs3',
                'SigmaCCDs3','lockts3','SIs3','SInums3','ps3','Ts1','Ts2','Ts3']
   
    data = pd.DataFrame(columns = varnames)

    for g in range(0,len(doy)):
        doy_temp = '{:03d}'.format(doy[g])
        for h in range(0,len(stat)):
            for i in range(0,len(hr)):
                for j in range(0,len(mn)):
                    if  exists(f'{dataworkspace_path}\\{stat[h]}{doy_temp}{hr[i]}{mn[j]}.{yr}_.ismr')==False:
                        if exists(dataworkspace_path)==False:
                            os.makedirs(dataworkspace_path)
                        if exists(f'{datalib_path}\\{stat[h]}{doy_temp}{hr[i]}{mn[j]}.{yr}_.ismr.gz'):
                            shutil.copy(f'{datalib_path}\\{stat[h]}{doy_temp}{hr[i]}{mn[j]}.{yr}_.ismr.gz', f'{dataworkspace_path}\\{stat[h]}{doy_temp}{hr[i]}{mn[j]}.{yr}_.ismr.gz')
                        else:
                             print(f'{stat[h]}{doy_temp}{hr[i]}{mn[j]}.{yr}_.ismr.gz does not exist')
                    if  exists(f'{dataworkspace_path}\\{stat[h]}{doy_temp}{hr[i]}{mn[j]}.{yr}_.ismr.gz'):
                        datatemp = pd.read_csv(f'{dataworkspace_path}\\{stat[h]}{doy_temp}{hr[i]}{mn[j]}.{yr}_.ismr.gz',compression='gzip',names=varnames)
                        data = pd.concat([data, datatemp], axis=0, ignore_index=True)
    
    times = timeISMR.timestamp(data)
    
    data['times'] = times #Inserts timestamps as column in dataframe
    
    return data
