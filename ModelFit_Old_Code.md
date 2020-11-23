# File for old Code
The code was tried in file `Sinkhole_Model_Fit_Tester.py

#intermezzo. Create A matrix with multiple R values
                        R_list = [10,20,30,50,70,100]
                        n_R_list = len(R_list)
                        n_r = len(r)

                        for i,iR in enumerate(R_list):
                            temp = np.zeros((n_R_list,n_r))
                            temp[i,:] = kinematicModel(iR,r)

                            temp = temp.T

                            # print(temp)
                            # input()

                            if i == 0:
                                A_matrix = temp
                            else:
                                A_matrix = np.concatenate((A_matrix,temp),axis=1)

                        # print(A_matrix.shape)
                        
                        a = np.linalg.cond(A_matrix)
                        print(a)

                        # A = np.reshape(A,(len(A),1))
                        # invQy = np.linalg.inv(np.eye(len(A))*self.sigmaInsar**2)
                        # Qxhat = np.linalg.inv(A.T @ invQy @ A)

                        if a > 1/sys.float_info.epsilon:
                            grid_counter[idx_y,idx_x] = 0
                        else:
                            grid_counter[idx_y,idx_x] = 1

                        # grid_counter[idx_y,idx_x] = a`
