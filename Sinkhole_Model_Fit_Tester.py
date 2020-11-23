'''
@author: Max Felius

TODO:
    1. Load the data
    2. Create grid
    3. Create design matrix A of sinkhole LSQ at grid point
    4. Get condition number of a matrix
    5. Save this conditional number
'''

#imports
import numpy as np
import pandas as pd
import os, sys, time
from decouple import config
from scipy import spatial
import rijksdriehoek2 as rijksdriehoek
import rijksdriehoek as rsd

class ModelFit(object):
    '''
    '''
    def __init__(self,file_in):
        '''
        '''
        #path variables
        self.file = file_in

        #variables
        self.resolution = 1 #[m] -> Tile is 80m
        self.xrange = None
        self.yrange = None
        self.xv = None
        self.yv = None
        self.data = None
        self.grid_polygon = []

        # Assumed variables
        self.R = [15] #[m] - Radius of a sinkhole
        self.sigmaInsar = 3/1000 #[m]

    def start(self):
        '''
        Execute steps
        '''
        #steps
        #1. Load the data
        self.Load_Data()

        #2. Create grid
        self.Create_Grid()

        #3. Create design matrix A
        self.build_design_matrix()

        #safe results
        return self.Create_df()
    
    def build_design_matrix(self):
        '''
        ROADMAP:
        1. Get locations of the points
        1.1. Get grid point
        1.2. filter all point out larger than 1.5*R using kdtree
        2. Compute the r vector
        3. Set up the A matrix
        4. compute A matrix condition number
        '''

        #time keeping
        start = time.time()

        kdtree = spatial.cKDTree(self.data.values)

        for R in self.R:
            radius = R
            grid_counter = np.zeros((len(self.yrange),len(self.xrange)))

            p = np.zeros((len(self.xrange),len(self.yrange),3))
            #step 1.1
            for idx_y,y in enumerate(self.yrange):
                for idx_x,x in enumerate(self.xrange):
                    #step 1.2
                    subset = kdtree.query_ball_point([x,y],r=radius)

                    #step 2 
                    if not subset:
                        r = 0
                    else:
                        rd = self.data.iloc[subset].values
                        r = np.sqrt((rd[:,0] - x)**2 + (rd[:,1] - y )**2)

                        #step 3

                    def kinematicModel(R,r):
                        return np.array((1/R**2)*np.exp(-np.pi*((r**2)/(R**2))))

                    # A = kinematicModel(R,r)

                    #step 4
                    if isinstance(r,int) or len(r) == 1:
                        grid_counter[idx_y,idx_x] = 0
                    else:
                        #intermezzo. Create A matrix with multiple R values
                        t = np.arange(5)
                        R_list = [R]#,20,30]
                        n_R_list = len(R_list)
                        n_r = len(r)

                        temp = np.zeros((len(t)*n_r*n_R_list,n_R_list*3))

                        for i,iR in enumerate(R_list):

                        # iR = 20

                            for it in t:
                                temp1 = np.array([kinematicModel(iR,r)*(it**2),kinematicModel(iR,r)*it,kinematicModel(iR,r)]).T
                                
                                if it ==0:
                                    temp2 = temp1
                                else:
                                    temp2 = np.concatenate((temp2,temp1),axis=0)
                                # print(temp2)
                                # input()

                            # print(n_r,n_R_list)
                            # print(temp2)
                            # print(temp2.shape)
                            # print(temp.shape)
                            
                             
                            # print(i)
                            # input()

                            temp[i*n_r*len(t):n_r*len(t)+i*n_r*len(t),i*3:3+i*3] = temp2

                            # temp = temp.T

                            # print(temp)
                            # input()

                            # if i == 0:
                            #     A_matrix = temp
                            # else:
                            #     A_matrix = np.concatenate((A_matrix,temp),axis=1)

                            # print(temp)
                            # input()
                        
                        a = np.linalg.cond(temp)

                        # print(a)
                        # print(temp2)
                        # input()
                        if a > 1/sys.float_info.epsilon:
                            grid_counter[idx_y,idx_x] = 0
                        else:
                            grid_counter[idx_y,idx_x] = 1

                        # grid_counter[idx_y,idx_x] = a
                    
                    #create a polygon of the entry
                    lbrd = rsd.Rijksdriehoek(x-self.resolution,y-self.resolution)
                    rbrd = rsd.Rijksdriehoek(x+self.resolution,y-self.resolution)
                    rtrd = rsd.Rijksdriehoek(x+self.resolution,y+self.resolution)
                    ltrd = rsd.Rijksdriehoek(x-self.resolution,y+self.resolution)

                    leftbot = lbrd.to_wgs()
                    rightbot = rbrd.to_wgs()
                    righttop = rtrd.to_wgs()
                    lefttop = ltrd.to_wgs()

                    self.grid_polygon.append(f'POLYGON (({leftbot[1]} {leftbot[0]},{rightbot[1]} {rightbot[0]},{righttop[1]} {righttop[0]},{lefttop[1]} {lefttop[0]}))')
                        

        self.grid_counter = grid_counter
        print(f'Elapsed time is {time.time()-start} seconds...')

    def Create_df(self):
        '''
        Output a dataframe that can be saved
        '''
        X = np.ravel(self.xv)
        Y = np.ravel(self.yv)
        Z = np.ravel(self.grid_counter)

        wgs = np.array(list(map(rijksdriehoek.rd_to_wgs,X,Y)))
    
        lat = wgs[:,0]
        lon = wgs[:,1]

        data_out = np.array([X,Y,lon,lat,Z,self.grid_polygon])

        return pd.DataFrame(data_out.T,columns=['rd_x','rd_y','lon','lat','Qxhat','geometry (wgs)'])

    def Load_Data(self):
        '''
        Step 1 -> loading data
        '''
        # path = config('data_folder')
        path = ''
        filename = self.file
        data = pd.read_csv(os.path.join(path,filename))

        self.data = data[['pnt_rdx','pnt_rdy']]

    def Create_Grid(self):
        '''
        Step 2 -> create grid
        '''
        max_x = max(self.data['pnt_rdx'])
        min_x = min(self.data['pnt_rdx'])

        max_y = max(self.data['pnt_rdy'])
        min_y = min(self.data['pnt_rdy'])

        resolution = self.resolution

        self.xrange = np.arange(min_x+resolution,max_x,resolution*2)
        self.yrange = np.arange(min_y+resolution,max_y,resolution*2)

        self.xv, self.yv = np.meshgrid(self.xrange,self.yrange)

def main():
    '''
    Apply to the whole dataset
    '''
    print('starting timer for t37')
    start = time.time()

    filenamet37 = 't37_points.csv'
    objt37 = ModelFit(filenamet37)

    dft37 = objt37.start()
    dft37.to_csv(f't37_detection_map_res200.csv')

    print('Done with track t37')
    print(f'Time elapsed is {time.time()-start} seconds')

    print('Starting with track t88')
    start = time.time()

    filenamet88 = 't88_points.csv'
    objt88 = ModelFit(filenamet88)

    dft88 = objt88.start()
    dft88.to_csv(f't88_detection_map_res200.csv')

    print('Done with track t88')
    print(f'Time elapsed is {time.time()-start} seconds')

def main2():
    '''
    Test the model on a urban area and a non-urban area
    '''
    print('Starting with the non-urban area')
    start = time.time()

    FILENAME = 't37_points_d500.csv'

    obj = ModelFit(FILENAME)
    # print(obj.grid_counter)

    df = obj.start()
    df.to_csv(f'ModelFit_d500_non-urban_R{obj.R[0]}_res{obj.resolution}.csv')

    print('Done with non-urban')
    print(f'Time elapsed is {time.time()-start} seconds')

    print('Starting with the urban area')

    start = time.time()

    FILENAME = 't37_points_d500_pastoorWijnenplein.csv'
    obj = ModelFit(FILENAME)

    df = obj.start()
    df.to_csv(f'ModelFit_d500_urban_R{obj.R[0]}_res{obj.resolution}.csv')

    print('Done with urban')
    print(f'Time elapsed is {time.time()-start} seconds')

def _test():
    '''
    Testing of the class pointCounter
    '''
    FILENAME = 't37_points_d500.csv'

    obj = ModelFit(FILENAME)
    # print(obj.grid_counter)

    df = obj.start()
    df.to_csv('Test_new_iR30_t10_s45.csv')

    # from mpl_toolkits.mplot3d import Axes3D  
    # # Axes3D import has side effects, it enables using projection='3d' in add_subplot
    # # import matplotlib.pyplot as plt
    # # import random

    # # def fun(x, y):
    #     # return x**2 + y

    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # # x = y = np.arange(-3.0, 3.0, 0.05)
    # # X, Y = np.meshgrid(x, y)
    # # zs = np.array(fun(np.ravel(X), np.ravel(Y)))
    # # Z = zs.reshape(X.shape)

    # ax.plot_surface(obj.xv, obj.yv, obj.grid_counter,cmap='jet')

    # ax.set_xlabel('X Label')
    # ax.set_ylabel('Y Label')
    # ax.set_zlabel('Z Label')

    # plt.show()

if __name__ == '__main__':
    main2()
    # _test()     