'''
@author: Max Felius
@date: 01/09/2020

This scripts reads the dataset and also makes a subset of that dataset if needed

Look at the _test function to see how to use this read data class
'''
#imports
import pandas as pd
import geopandas as gpd
import sys
import time
import re
from scipy import spatial
from rijksdriehoek import Rijksdriehoek

class dataset:
    '''
    INPUT FORMATS SUPPORTED:
    - csv (default)
    - shp
    
    INPUT DATE FORMATS SUPPORTED:
    - S1 (default)
    - rs2
    '''
    def __init__(self,file_in,format='csv',data_format='s1'):
        '''
        :type file_in: string
        :rtype: None
        '''
        self.file = file_in

        #select correct date format for header search
        self.filter_option,self.coordinates = self.select_filter(data_format)

        #read from correct format
        if format.lower() == 'csv':
            #read data and other variables
            self.data, self.header, self.epochs = self.read_data_csv(self.file,self.filter_option)
        elif format.lower() == 'shp':
            #read data from shapefile
            self.data, self.header, self.epochs = self.read_data_shp(self.file,self.filter_option)
        else:
            print(f'Format: {format} is not supported yet. Please select a supported format (csv or shp)...')
            sys.exit('Quitting the program now')

        #if the data_format is RS2 then rdx and rdy have to be computed
        if data_format.lower() == 'rs2':
            rd = rijksdriehoek.Rijksdriehoek()
            rd.from_wgs(self.data[self.coordinates[1]],self.data[self.coordinates[0]])

            self.data = self.data.join(pd.DataFrame({'rd_x':rd.rd_x,'rd_y':rd.rd_y},index=self.data.index))
            self.coordinates = self.coordinates + ['rd_x','rd_y']
            self.header = self.header + ['rd_x','rd_y']

        #initializing the kdtree
        #input coordinates are in Rijksdriehoek
        self.data_kdtree = self.init_kdtree(self.data,self.coordinates[2:])

        print('\nFinished reading the data set and creating the data object.\n')

    def select_filter(self,platform):
        '''
        To add a new sensor to the method is easy. Make another elif statement and write down the correct
        regex code. The second argument to return is the coordinate header names. If rd is not included,
        make an extra elif statement in __init__.

        :type platform: string
        :rtype: regex object
        :rtype: list
        '''

        if platform.lower() == 's1':
            print('Using date format and coordinate selection for sentinel-1 (s1) data')
            return re.compile(r'd_\d{8}'), ['pnt_lon','pnt_lat','pnt_rdx','pnt_rdy']
            #return 'd_20'
        elif platform.lower() == 'rs2':
            print('Using date format and coordinate selection for rs2 data')
            return re.compile(r'\d{2}-\D{3}-\d{4}'), ['lon','lat']
        else:
            print(f'Platform {platform} is not support. Please select a supported format...')
            sys.exit('Quitting the program now')

    def read_data_shp(self,file,filter_string):
        '''
        :type file: string
        :type filter_string: regix object
        :rtype: pandas dataframe, list[], list[]
        '''
        start = time.time()
        print(f'Started Reading Input Shapefile {file}...')
        data = gpd.read_file(file)
        print(f'finished reading Input Shapefile in {time.time()-start} seconds...')

        return data, list(data), list(filter(lambda x: filter_string.match(x) != None, list(data)))

    def read_data_csv(self,file,filter_string):
        '''
        :type file: string
        :type filter_string: regex object
        :rtype: pandas dataframe, list[], list[]
        '''
        start = time.time()
        print(f'Started Reading Input csv file {file}')
        data = pd.read_csv(file,sep=',',header=0)
        print(f'Finished Reading Input csv file in {time.time()-start} seconds...')

        return data, list(data), list(filter(lambda x: filter_string.match(x) != None, list(data)))

    def init_kdtree(self,data,header):
        '''
        :type data: pandas dataframe
        :type header: list[string]
        :rtype: KDTree object
        '''
        print('Initializing KD-Tree')
        #print('WARNING: make sure to use rijksdriehoek coordinates for spatial coordinate selection')
        #extracting values out of data and put it into np.array
        tree = spatial.cKDTree(data[header].values)

        return tree

    def create_subset(self,point,search_radius):
        '''
        :type point: list[float, float]
        :type search_radius: int
        :rtype: pandas DataFrame
        '''

        print(f'Creating subset using the KD-Tree with center = {point} and search radius = {search_radius}')
        
        subset = self.data_kdtree.query_ball_point(point,r=search_radius)

        #print('WARNING: make sure to use rijksdriehoek coordinates for the point and search_radius in meters')

        return pd.DataFrame(self.data.values[subset],columns=self.header)

def _test():
    '''
    '''
    FILENAME = 't37_points.csv'

    obj = dataset(FILENAME,format='csv',data_format='s1')

    point = [203338.4, 319520.3]

    radius = 30

    df = obj.create_subset(point,radius)

    df.to_csv(f't37_points_d{radius}_pastoorWijnenplein.csv')

    print('Done')

if __name__ == '__main__':
    _test()
