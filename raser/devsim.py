# -*- encoding: utf-8 -*-
import os


class Devsimcal:
    def __init__(self, my_d, dev_dic):
        self.det_model = dev_dic['det_model']
        self.dl_x = my_d.l_x/dev_dic['xyscale']
        self.dl_y = my_d.l_y/dev_dic['xyscale']
        self.dl_z = my_d.l_z
        self.electrode_total_number = dev_dic['electrode_total_number']

        self.tol = 1e-14
        self.bias_voltage = my_d.voltage

        filepath = './output/devsim/1D_NJU_PIN/500.0V_x_E.csv'
        self.depth, self.elefield, self.protential = self.readfield(filepath, 
                                                                    self.dl_z)


    def readfield(filepath, zmax):
        depth, elefield, protential = [], []
        with open(filepath, 'r') as f:
            for line in f.readlines():
                try:
                    fargs = list(map(float, 
                                     line.strip('\n').strip().split(',')))
                    depth.append(fargs[0])
                    elefield.append(fargs[1])
                    protential.append(1 - fargs[0]/zmax)
                    
                except Exception as e:
                    print(filepath + ' has been read.')
                    pass
        
        return depth, elefield


    