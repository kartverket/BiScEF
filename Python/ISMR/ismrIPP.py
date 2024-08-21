# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 10:19:37 2022

@author: saschu
"""

import math

def IPP_test(data,network,stat,ionoHeight):
    
    
    with open('All_stations.csv') as fh:
        for line in fh:
            if stat in line:
                k=[x for x in line.split(',')]
                lat_r = float(k[1])
                lon_r = float(k[2])
                
    el = data['Elevation'].values*(math.pi/180)
    az = data['Azimuth'].values*(math.pi/180)
    Re = 6371
    Hip = ionoHeight
    
   
    Gamma = [0]*len(el)
    lat_ip = [0]*len(el)
    lon_ip = [0]*len(el)
    
    for i in range(0,len(el)):
        Gamma[i] = (math.pi/2)-el[i]-math.asin((Re/(Re+Hip))*math.cos(el[i]))
    
        lat_ip[i] = math.asin(math.sin(lat_r*(math.pi/180))*math.cos(Gamma[i])+math.cos(lat_r*(math.pi/180))*math.sin(Gamma[i])*math.cos(az[i]))*(180/math.pi)
    
        lon_ip[i] = lon_r+math.asin(math.sin(Gamma[i])*math.sin(az[i])/math.cos(lat_ip[i]*(math.pi/180)))*(180/math.pi)
    
    return lon_ip, lat_ip
                
