'''
@author: Max Felius

Script for creating detectability maps whereby the minimum detectable sinkhole radius will be determined.

# ROADMAP
1. Load the data (note: check for presence of rd coordinates)
2. Subdivide area into 4 block
3. Determine possibility of a sinkhole in that block
    3.1 if yes, subdivide block into 4 subblocks -> goto 3
    3.2 if no, create polygon with R set to block diameter

'''

#imports
import numpy as np
import pandas as pd
import time, os, sys, datetime
from scipy import spatial

class detectability_map:
    '''
    '''
    def __init__(self,filename):
        '''
        Coordinates headers are: 'pnt_rdx','pnt_rdy'
        '''
        self.filename = filename
        self.data = pd.read_csv(self.filename)

    def block_tester(self):
        '''
        '''
        rdx_max = max(self.data['pnt_rdx'])
        rdx_min = min(self.data['pnt_rdx'])
        rdy_max = max(self.data['pnt_rdy'])
        rdy_min = min(self.data['pnt_rdy'])

        mid_x = (rdx_max + rdx_min)/2
        mid_y = (rdy_max + rdy_min)/2

        radius = max(mid_x,mid_y)

        p1 = 0
        p2 = 0
        p3 = 0
        p4 = 0

def main():
    '''
    Main function to create the detectability maps
    '''
    pass

def _test():
    '''
    Function to test the detectability_map class

    '''
    filename = 'name.csv'

    obj = detectability_map(filename)

if __name__ == '__main__':
    _test()

