'''
@author: Max Felius

Making a square subset area with specified dimensions
'''

#import
import numpy as np
from matplotlib import pyplot as plt
import os, time, sys
import pandas as pd
from decouple import config #install package by running: 'python -m pip install django-decouple'
import re

class subset_creator:
    '''
    Class to easily make subsets
    '''
    def __init__(self,subset_radius,filename,lon,lat,save_full_dataset=False):
        '''
        Initialize the object
        '''
        #imports from object creation
        self.import_file = filename
        self.radius = subset_radius
        self.lat = lat
        self.lon = lon

        #saving full dataset means saving also the column other than the lat and lon columns
        self.save_full_dataset = save_full_dataset

        #import the data
        start = time.time()
        print(f'Reading the data')
        self.data = pd.read_csv(self.import_file)
        print('Finished reading the data in {:.02f} seconds.'.format(time.time()-start))

        #Create filtered Dataset
        filt_dataset = self.create_subset()

        #Save filtered dataset
        self.save_subset(filt_dataset)

    def create_subset(self):
        '''
        Method that creates the subset from the larger subset
        '''
        print(f'Location: lat {self.lat}, lon {self.lon}. Radius selected: {self.radius} meter.')

        R = 6371000 # [m], radius of the Earth
        self.theta = np.rad2deg(2 * np.arcsin(self.radius/R))

        if self.save_full_dataset:
            header = list(self.data)
        else:
            header = ['id','pnt_lon','pnt_lat']

        df_out = pd.DataFrame(columns=header)
        start = time.time()

        print('Starting to filter the points...')
        for i in range(len(self.data)):
            temp = self.data.iloc[i]
            if temp['pnt_lat'] <= self.lat+self.theta and temp['pnt_lat'] >= self.lat-self.theta and temp['pnt_lon'] <= self.lon + self.theta and temp['pnt_lon'] >= self.lon-self.theta:
                idName = temp['id']
                print(f'Added point {idName}')
                df_out = df_out.append(temp[header],ignore_index=True)

        print('Finished Filtering the points in {:.02f} seconds.'.format(time.time()-start))
        return df_out

    def save_subset(self,dataset):
        '''
        Method to save the subset 
        '''
        filename_out = 'subset_r{}_lon{:.02f}_lat{:.02f}.csv'.format(self.radius,self.lon,self.lat)
        print(f'Saving file with radius {self.radius} and center points lon={self.lon} and lat={self.lat}.')
        
        #folder to create the subset in
        if not os.path.exists('subsets'):
           print('Created subsets folder for subset saving')
           os.mkdir('subsets')

        dataset.to_csv(os.path.join('subsets',filename_out))
        print(f'Finished saving the file: {filename_out}')

def _test():
    #data locations
    path_mrss = config('MRSS')
    filename = 'full-pixel_mrss_s1_asc_t88_v4_080a1cbf7de1b6d42b3465772d9065fe7115d4bf.csv'

    filename_in = os.path.join(path_mrss,filename)
    radius = 1000 #1km

    #center coordinates
    '''
    Rotonde
    - Wijngracht
    - Caspar Sprokelstraat
    - Koningsweg
    '''
    lon = 6.05879
    lat = 50.86837

    save_full_dataset=False

    subset_creator(radius,filename_in,lon,lat,save_full_dataset)

def main():
    pass

if __name__ == '__main__':
    _test()