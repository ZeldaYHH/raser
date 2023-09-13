#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   devsim.py
@Time    :   2023/06/04
@Author  :   Henry Stone 
@Version :   1.0
'''

import os
import csv
from scipy.interpolate import interp1d
from scipy.interpolate import interp2d
import math
import pickle

class DevsimCal:
    def __init__(self, my_d,det_name,det_dic,dev_dic):
        self.voltage = my_d.voltage
        self.protential = []
        self.l_z = my_d.l_z
        self.read_ele_num = dev_dic['read_ele_num']        
        self.lz = []
        self.elefield = []
        self.gradu = []
        self.flag_2d = False
        print("init\n")
        if(det_name=="NJU-PIN"):
            e_field_filepath = './output/devsim/1D_NJU_PIN/'+ str(-int(det_dic['voltage'])) + '.0V_x_E.csv'
            self.readfile(e_field_filepath)
        elif(det_name==""):
            e_field_filepath = './output/devsim/1D_NJU_PIN/'+ str(-int(det_dic['voltage'])) + '.0V_x_E.csv'
            self.readfile(e_field_filepath)
        elif(det_name=="SICAR-1"):
            self.flag_2d = True
            potential_path = './output/devsim/2D_SICAR/' + str(-int(det_dic['voltage'])) + 'V_potential.pkl'
            self.read_pickle(potential_path)
        

    def readfile(self, e_field_filepath):
        i = 0
        with open(e_field_filepath, 'r') as f:
            for line in f.readlines():
                try:
                    fargs = list(map(float, 
                                     line.strip('\n').strip().split(',')))
                    self.lz.append(fargs[0]*1e4) #cm->um
                    self.elefield.append(fargs[1]/1e4) #V/cm -> V/um         
                except Exception as e:
                    pass
        self.gradu.append([])
        self.gradu.append([])
        self.gradu.append([])
        self.gradu[2].append(0)
        grad = self.voltage
        for i in range(len(self.elefield)-1):
            grad = grad - (self.elefield[i]+self.elefield[i+1]) * \
                            (self.lz[i+1]-self.lz[i]) / 2
            self.gradu[2].append(grad)

    def get_e_field(self, x, y, depth):    
        if self.flag_2d:    
            f_efx = interp1d(self.elefield[0], self.elefield[2], 
                            kind='linear', fill_value="extrapolate")
            f_efz = interp1d(self.elefield[1], self.elefield[3], 
                            kind='linear', fill_value="extrapolate")
            return f_efx(x), 0, f_efz(depth) 
        else:
            f_efz = interp1d(self.lz, self.elefield, 
                            kind='linear', fill_value="extrapolate")
            return 0, 0, f_efz(depth) #x, y方向为0
    
    def get_w_p(self, x, y, depth, i):
        if depth >= 1:
            f_p = 1 - (1/(self.l_z-1)) * (depth-1)
        else:
            f_p = 0
        return f_p
    
    def get_potential(self, x, y, depth):
        f_u = interp2d(self.gradu[0], self.gradu[1], self.gradu[2], 
                       kind = 'linear', fill_value="extrapolate")
        return f_u(x, depth)
    
    def read_pickle(self, potential_path):
        with open(potential_path, 'rb') as f:
            self.gradu = pickle.load(f)
        self.gradu = sorted(self.gradu, key=(lambda x:[x[1], x[0]]))
        lz = self.gradu[1][0]
        lx = self.gradu[0][0]
        for i in range(len(self.gradu[0])-2):
            if self.gradu[1][i+1] > lz:
                self.elefield.append(self.elefield[i-1])
                lz = self.gradu[1][i+1]
            else:
                potential_x = (self.gradu[2][i+1]-self.gradu[2][i]) / (self.gradu[0][i+1]-self.gradu[0][i])
                self.elefield.append([self.gradu[0][i], self.gradu[1][i], potential_x, 0])

        sorted(self.gradu, key=(lambda x:[x[0], x[1]]))
        lz = self.gradu[0][1]
        lx = self.gradu[0][0]
        for i in range(len(self.gradu[0])-1):
            if self.gradu[1][i+1] > lx:
                self.elefield[i] = self.elefield[i-1]
                lx = self.gradu[0][i+1]
            else:
                potential_z = (self.gradu[2][i+1]-self.gradu[2][i]) / (self.gradu[1][i+1]-self.gradu[1][i])
                try:
                    self.elefield[i][3] = potential_z
                except:
                    print("error")

        
