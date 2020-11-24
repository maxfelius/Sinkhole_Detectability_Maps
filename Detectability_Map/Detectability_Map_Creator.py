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
from tqdm import tqdm

from decouple import config

#import package files
# from Detectability_Map.read_sentinel1_csv_data import dataset
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


        # print(f'Started reading data file: {filename}')
        self.dataset_obj = dataset(self.filename)
        # print(f'Finished reading the dataset')

        #extracting variables from object
        self.extend_rd = self.dataset_obj.extend_rd #[min x, max x, min y, max y]
        self.extend_wgs = self.dataset_obj.extend_wgs #[min lon, max lon, min lat, max lat]
        self.header = self.dataset_obj.header
        self.epochs = self.dataset_obj.epochs

    def make_map(self,R,S,x_eval,y_eval):
        '''
        Method to create the detectability map. Input are the evaluation coordinates and the radius of infuence.

        Input:
        :type R: int
        :type S: int
        :type x_eval: list[float]
        :type y_eval: list[float]

        Output:
        :rtype list[boolean]
        '''
        range_len = len(x_eval)

        return_result = np.zeros((range_len,1))

        for i in tqdm(range(range_len),desc='Making the Map...'):
            x_pos = x_eval[i]
            y_pos = y_eval[i]

            #NOTE: Check if x_pos is the first value
            location = [x_pos, y_pos]
            radius = R
            # print('Retrieving subset')
            subset = self.dataset_obj.create_spatial_subset(location,radius)
            # subset = self.dataset_obj.data[subset_idx]
            # print('Checking subset for solution')
            return_result[i] = self.check_subset(subset,S,R,x_pos,y_pos)

        return return_result

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

        # print('Computing the radius.')
        r = np.sqrt((subset['pnt_rdx']-x0)**2 + (subset['pnt_rdy']-y0)**2)

        # print('Making Design Matrix.')
        design_matrix = np.array([(1/R**2)*np.exp(-np.pi*(r**2/R**2))])

        # print('Computing the conditional number.')

        if len(design_matrix)==0:
            return 0
        else:
            cond_number = np.linalg.cond(design_matrix)

        # print('Check the magnitude of the conditional number.')
        if cond_number > 1/sys.float_info.epsilon:
            return 0
        else:
            return 1

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

    #parameters
    n = 100
    w = 1
    M = 1
    H = 10
    zone_angle = np.deg2rad(35)
    w_c = H/np.cos(zone_angle)

    S = (2*M*w)/(w+w_c)
    R = 10 #[m]

    coordinates = obj.extend_rd
    xmin = coordinates[0]
    xmax = coordinates[0]+(coordinates[1]-coordinates[0])*0.001

    x_range = np.linspace(xmin,xmax,n)

    ymin = coordinates[2]
    ymax = coordinates[2]+(coordinates[3]-coordinates[2])*0.001

    y_range = np.linspace(ymin,ymax,n)

    xv,yv = np.meshgrid(x_range,y_range)

    x_eval = xv.ravel()
    y_eval = yv.ravel()

    image_out = obj.make_map(R,S,x_eval,y_eval)

    print(image_out.shape)
    print(image_out)

    image = image_out.reshape((len(y_range),len(x_range)))
    plt.imsave(f'Detectability_map_{R}.tiff',image)


if __name__ == '__main__':
    _test()
