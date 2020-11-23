'''
@author: Max Felius

Script for creating detectability maps whereby the minimum detectable sinkhole radius will be determined.
'''

#imports
import numpy as np
import pandas as pd
import time, os, sys, datetime
from scipy import spatial
import matplotlib.pyplot as plt
import progressbar

from decouple import config

#import package files
from Detectability_Map.read_sentinel1_csv_data import dataset

class detectability_map:
    '''
    '''
    def __init__(self,filename):
        '''
        Coordinates headers are: 'pnt_rdx','pnt_rdy'
        '''
        self.filename = filename

        #detectability map parameters


        print(f'Started reading data file: {filename}')
        self.dataset_obj = dataset(self.filename)
        print(f'Finished reading the dataset')

        #extracting variables from object
        self.extend_rd = self.dataset_obj.extend_rd #[min x, max x, min y, max y]
        self.extend_wgs = self.dataset_obj.extend_wgs #[min lon, max lon, min lat, max lat]
        self.header = self.dataset_obj.header
        self.epochs = self.dataset_obj.epochs

    def check_subset(self,subset,S,R,x0,y0):
        '''
        Checks if a subset has a solvable design matrix

        Input:
        :type subset: pandas dataframe
        :type S: int
        :type R: int
        :type x0: int
        :type y0: int

        Output
        :rtype: boolean
        '''

        r = np.sqrt((subset['pnt_rdx']-x0)**2 + (subset['pnt_rdy']-y0)**2)

        design_matrix = np.array([(1/R**2)*np.exp(-np.pi*(r**2/R**2))])

def main():
    '''
    Main function to create the detectability maps
    '''
    pass

def _test():
    '''
    Function to test the detectability_map class

    '''
    mrss = config('MRSS')
    dataset_filename = os.path.join(mrss,'full-pixel_mrss_s1_asc_t88_v4_080a1cbf7de1b6d42b3465772d9065fe7115d4bf.csv')

    obj = detectability_map(dataset_filename)

if __name__ == '__main__':
    _test()
