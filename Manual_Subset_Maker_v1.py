#!python3
'''
@author: Max Felius
@email: maxfelius@hotmail.com

Plot sinkhole locations with an area of sar point. Check whether a acceleration around a particular sinkhole is visible

Version v2
'''

#import
import numpy as np
from matplotlib import pyplot as plt
import geopandas as gpd
import os, time
import pandas as pd
from decouple import config #install package by running: 'python -m pip install django-decouple'

#which track do we want to process? Set track to True is you want to process the track
track_88 = False
track_37 = True 

#data locations
path_t88 = config('path88')
path_t37 = config('path37')

#Global variables
radius = 100 #[m] -> Radius

#read the location
location = pd.read_csv('sinkhole_kerkrade.csv')

R = 6371000 # [m]
theta = np.rad2deg(2 * np.arcsin(radius/R))

#need to edit this
lat = location.iloc[0][0]
lon = location.iloc[0][1]
name = location.iloc[0][2]

print(f'Location: lat {lat}, lon {lon}, name {name}. Radius selected: {radius} meter.')

if track_88:
    #import sar points
    print('Reading t88 data...')
    start = time.time()
    t88_data = gpd.read_file(os.path.join(path_t88,'limburg_t88.shp'))
    print(f'Elapsed time {time.time()-start}')

if track_37:
    #import sar points
    print('Reading t37 data...')
    start = time.time()
    t37_data = gpd.read_file(os.path.join(path_t37,'limburg_t37.shp'))
    print(f'Elapsed time {time.time()-start}')

#extract column headers
header1 = []
header2 = []

for col in t88_data: header1.append(col)
for col in t37_data: header2.append(col)
# header_epochs = list(filter(lambda x: x.startswith('d_20'),header1))

if track_88:
    t88_points = pd.DataFrame(columns=header1)
    start = time.time()
    print('Filtering the points for t88...')
    for i in range(len(t88_data)):
        temp = t88_data.iloc[i]
        if temp['pnt_lat'] <= lat+theta and temp['pnt_lat'] >= lat-theta and temp['pnt_lon'] <= lon + theta and temp['pnt_lon'] >= lon-theta:
            idName = temp['id']
            print(f'Added point {idName}')
            t88_points = t88_points.append(temp,ignore_index=True)

    print(f'Elapsed time {time.time()-start}')

    #save file
    name_out = f't88_points_{name}_r{radius}.csv'
    t88_points.to_csv(name_out)
    print(f'{name} file saved...')

if track_37:
    t37_points = pd.DataFrame(columns=header2)
    start = time.time()
    print('Filtering the points for t37...')
    for i in range(len(t37_data)):
        temp = t37_data.iloc[i]
        if temp['pnt_lat'] <= lat+theta and temp['pnt_lat'] >= lat-theta and temp['pnt_lon'] <= lon + theta and temp['pnt_lon'] >= lon-theta:
            idName = temp['id']
            print(f'Added point {idName}')
            t37_points = t37_points.append(temp,ignore_index=True)

    print(f'Elapsed time {time.time()-start}')

    #save file
    name_out = f't37_points_{name}_r{radius}.csv'
    t37_points.to_csv(name_out)
    print(f'{name} file saved...')

