'''
@author: Max Felius

Main file to create the settings for the detectability maps.

This script will make the multiple detectability maps, stores the maps and convolutes the maps.
'''

#imports
import os,sys,time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from decouple import config

#import package
sys.path.extend(os.path.join(os.getcwd(),'Detectability_Map'))

#package imports
# from read_sentinel1_csv_data import dataset
from Detectability_Map.Detectability_Map_Creator import detectability_map

class make_maps:
    '''
    '''
    def __init__(self,filename,location,R_list):
        '''
        Initializing the object

        Input:
        - datafile and location
        - range of R on which it should be evaluated

        :type filename: string
        :type location: string
        '''
        #save the parameters
        self.filename = filename
        self.location = location
        self.R_list = R_list

        #check if data is available
        if not os.path.exists(os.path.join(location,filename)):
            sys.exit(f'File {filename} does not exist.')

        #check if data folder is available
        if not os.path.exists('data'):
            print('Created the data folder.')
            os.mkdir('data')
        
        #create data folder if not exists
        if not os.path.exists(os.path.join('data',filename[:-4])):
            print(f'Create the data folder for the results of {filename}.')
            os.mkdir(os.path.join('data',filename[:-4]))
        else:
            print(f'Data folder for {filename} already exists.')
        
        print(f'Total of {len(R_list)} maps will be created.')

        #Importing the dataset into the detectability map object
        dataset_filename = os.path.join(location,filename)
        obj = detectability_map(dataset_filename)

        #sinkhole parameters 
        n = 100
        w = 1
        M = 1
        H = 10
        zone_angle = np.deg2rad(35)
        w_c = H/np.cos(zone_angle)
        S = (2*M*w)/(w+w_c)

        #test value
        R = R_list[0]

        #creating the evaluation grid
        coordinates = obj.extend_rd
        xmin = coordinates[0]
        xmax = coordinates[1]
        x_range = np.arange(xmin,xmax,R/2)

        ymin = coordinates[2]
        ymax = coordinates[3]
        y_range = np.arange(ymin,ymax,R/2)

        xv,yv = np.meshgrid(x_range,y_range)

        x_eval = xv.ravel()
        y_eval = yv.ravel()

        image_out = obj.make_map(R,S,x_eval,y_eval,len(x_range),len(y_range))

        image = image_out.reshape((len(y_range),len(x_range)))
        
        print('Saved Image')
        plt.imsave(f'Detectability_{R}.tiff',image)

def _test1():
    '''
    '''
    location = config('MRSS')
    filename = 'full-pixel_mrss_s1_asc_t88_v4_080a1cbf7de1b6d42b3465772d9065fe7115d4bf.csv'
    R_list = [30]

    make_maps(filename,location,R_list)

if __name__ == '__main__':
    _test1()
