'''
@author: Max Felius
@date: 12/11/2020

This script will read sentinel-1 csv data provided by Skygeo

This script will create an object with the data in it. For example creating subsets and retrieving important headers will be made simple.
'''
#imports
import pandas as pd
import numpy as np
import sys, os
import time
import re
from scipy import spatial

sys.path.extend(os.getcwd())
from read_data.rijksdriehoek import Rijksdriehoek

class dataset:
    '''
    Object that reads and holds the input dataset

    In this object the RD coordinates are also added to the dataset.

    Output coordinate sets are RD and WGS
    '''
    def __init__(self,file_in):
        '''
        :type file_in: string
        '''
        self.file = file_in

        #options
        self.filter_option = re.compile(r'd_\d{8}')
        self.coordinates = ['pnt_lon','pnt_lat','pnt_rdx','pnt_rdy']

        start = time.time()
        print(f'Starting to read the data: {self.file}.')

        #retrieving the data
        self.data, self.header, self.epochs = self.read_data_csv(self.file,self.filter_option)

        #appending two newly created headers
        self.header.append('pnt_rdx')
        self.header.append('pnt_rdy')

        #add rijksdriehoek coordinates to the dataset
        rd_data = self.convertSPHE2RD(self.data[self.coordinates[:2]])
        self.data = self.data.join(rd_data)

        #creating the kdtree for easy and quick subset extraction
        self.data_kdtree = self.init_kdtree(self.data,self.coordinates[2:])

        print(f'Finished Loading the dataset in {time.time()-start} seconds...')

        #some handy variables
        self.extend_wgs = [min(self.data['pnt_lon']),max(self.data['pnt_lon']),min(self.data['pnt_lat']),max(self.data['pnt_lat'])]
        self.extend_rd = [min(self.data['pnt_rdx']),max(self.data['pnt_rdx']),min(self.data['pnt_rdy']),max(self.data['pnt_rdy'])]

    def convertSPHE2RD(self,data):
        '''
        '''
        # wgs_obj = rijksdriehoek.Rijksdriehoek()
        wgs_obj = Rijksdriehoek()

        wgs_obj.from_wgs(data['pnt_lat'],data['pnt_lon'])
        rdata = np.array([wgs_obj.rd_x,wgs_obj.rd_y]).T

        return pd.DataFrame(rdata,columns=['pnt_rdx','pnt_rdy'])

    def read_data_csv(self,file,filter_string):
        '''
        :type file: string
        :type filter_string: regex object
        :rtype: pandas dataframe, list[], list[]
        '''
        data = pd.read_csv(file,sep=',',header=0)

        return data, list(data), list(filter(lambda x: filter_string.match(x) != None, list(data)))

    def init_kdtree(self,data,header):
        '''
        :type data: pandas dataframe
        :type header: list[string]
        :rtype: KDTree object
        '''
        tree = spatial.cKDTree(data[header].values)

        return tree

    def create_subset(self,point,search_radius):
        '''
        :type point: list[float, float]
        :type search_radius: int
        :rtype: pandas DataFrame
        '''
        start = time.time()
        print(f'Creating subset using the KD-Tree with center = {point} and search radius = {search_radius}')
        subset = self.data_kdtree.query_ball_point(point,r=search_radius)

        print(f'Finished creating the subset. Time: {time.time()-start} seconds.')
        return pd.DataFrame(self.data.values[subset],columns=self.header)

def _test():
    '''
    Simple test function
    '''
    from decouple import config
    import matplotlib.pyplot as plt
    path88 = config('MRSS')

    dataset_filename = os.path.join(path88,'full-pixel_mrss_s1_asc_t88_v4_080a1cbf7de1b6d42b3465772d9065fe7115d4bf.csv')

    obj = dataset(dataset_filename)

    location = [203338.4, 319520.3]
    radius = 100
    subset = obj.create_subset(location,radius)

    plt.figure()
    plt.scatter(subset['pnt_rdx'],subset['pnt_rdy'])
    plt.show()

def _test1():
    '''
    Simple test function with beeps
    '''
    import beepy
    try:
        from decouple import config
        import matplotlib.pyplot as plt
        path88 = config('MRSS')

        dataset_filename = os.path.join(path88,'full-pixel_mrss_s1_asc_t88_v4_080a1cbf7de1b6d42b3465772d9065fe7115d4bf.csv')

        obj = dataset(dataset_filename)

        location = [203338.4, 319520.3]
        radius = 100
        subset = obj.create_subset(location,radius)

        print(f'Extend of the coordinates (wgs) is: {obj.extend_wgs}')

        beepy.beep(sound='coin')

        plt.figure()
        plt.scatter(subset['pnt_rdx'],subset['pnt_rdy'])
        plt.show()
        
    except Exception as e:
        print('error',e)
        beepy.beep(sound='error')

if __name__ == '__main__':
    _test1() #with the beepy sound
