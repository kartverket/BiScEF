# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 15:22:05 2022

@author: saschu
"""
import pandas as pd
from datetime import datetime

def timestamp(data):
    
    datum = datetime(1980,1,6,0,0,0)
    newdays = datum + pd.to_timedelta(data.GPSweek*7, unit='days')
    newtime = newdays + pd.to_timedelta(data.TOW, unit='second')
    
    return newtime
    

    
    