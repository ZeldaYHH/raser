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
import math
import pickle
import ROOT
import numpy as np


class Devsim_field:
    def __init__(self, my_d,det_name,det_dic,dev_dic,dimension):
        self.voltage = my_d.voltage
        self.l_z = my_d.l_z
        self.read_ele_num = int(dev_dic['read_ele_num']) 
        self.w_p=[]
        self.name = det_name
        self.dimension = dimension
        if(det_name=="Si_Strip"):
            with open("./output/testdiode/x.pkl",'rb') as file:
                x=pickle.load(file)
            with open("./output/testdiode/y.pkl",'rb') as file:
                y=pickle.load(file)
            with open("./output/testdiode/potential_{}.pkl".format(self.voltage),'rb') as file:
                potential=pickle.load(file)
            self.x_efield,self.y_efield,self.potential=get_field_2d(x,y,potential)
            for i in range(int(self.read_ele_num)):
                self.w_p.append(strip_w_p(i))

        if(det_name=="SICAR-1"):
            if dimension == 2:
                with open("output/devsim/2D_SICAR/80V_potential.pkl",'rb') as file:
                    xypotension=pickle.load(file)
                    x=xypotension[0]
                    y=xypotension[1]
                    potential=xypotension[2]
                    self.x_efield,self.y_efield,self.potential=get_field_2d(x,y,potential)
            elif dimension == 1:
                pass
            else:
                raise ValueError('unexpect dimension')
            
        if(det_name=='NJU-PIN'):
            if dimension == 2:
                pass
            elif dimension ==1:
                with open("output/devsim/field/NJU-PIN/") as file:
                    z = pickle.load(file)[0]
                    field = pickle.load(file)[1]
                    self.efield=get_field_1d(z, field)
            else:
                raise ValueError('unexpect dimension')
            
    def get_e_field(self, x, y, depth):
        if self.dimension == 2:
            f_efx = self.x_efield.Interpolate(depth,x)
            f_efz = self.y_efield.Interpolate(depth,x)
            return f_efz, 0, f_efx            
        else:
            f_e = self.efield.Eval(depth)
            return f_e, 0, f_e
    
    def get_w_p(self, x, y, depth, i):
        if self.name == 'Si_Strip':
            return self.w_p[i].Interpolate(x,depth)
        else:
            return linearity_w_p(depth)
    
    def get_potential(self, x, y, depth):
        f_u = self.potential.Interpolate(depth,x)
        return f_u

def get_field_1d(z, field):
    efield = ROOT.TGraph()
    for i in range(len(z)):
        efield.SetPoint(len(z), z[i], field[i])
    z = ROOT.TGraph()

    graph=ROOT.TF1("linearFit", "pol1", np.min(z), np.max(z))
    z.Fit(graph, 'Q')
    return z

def get_field_2d(x,y,potential):
    x_efield=[]
    y_efield=[]
    x_u=np.unique(x)
    y_u=np.unique(y)
    reorganization_potential=[]
    for i in range(len(x_u)):
        temporary_potential=[]
        for j in range(len(x)):
            if x_u[i]==x[j]:
                temporary_potential.append(potential[j])
        reorganization_potential.append(temporary_potential)
    for i in range(len(reorganization_potential)-1):
        grad=np.gradient(np.array([reorganization_potential[i], reorganization_potential[i+1]], dtype=np.float))
        x_efield.append(grad[0][1])
        y_efield.append(grad[1][0])
        if i == (len(reorganization_potential)-2):
            y_efield.append(grad[1][1])
            x_efield.append(np.gradient(reorganization_potential[i+1]))
    print(np.max(x_efield))
    re_potential=ROOT.TGraph2D()
    x_field=ROOT.TGraph2D()
    y_field=ROOT.TGraph2D()
    print(np.max(reorganization_potential))
    for i in range(len(x_u)):
        for j in range(len(y_u)):
            x_field.SetPoint(int(i*len(y_u)+j), x_u[i]*1e4, y_u[j]*1e4, x_efield[i][j]/3)
            y_field.SetPoint(int(i*len(y_u)+j), x_u[i]*1e4, y_u[j]*1e4, y_efield[i][j]/3)
            re_potential.SetPoint(int(i*len(y_u)+j), x_u[i]*1e4, y_u[j]*1e4, reorganization_potential[i][j])
    
    return x_field,y_field,re_potential

def strip_w_p(ele_number):
    nx = 51  
    ny = 226  
    xmin, xmax = 0.0, 50.0  
    ymin, ymax = 0.0, 225.0 
    dx = (xmax - xmin) / (nx - 1)  
    dy = (ymax - ymin) / (ny - 1) 

    u = np.zeros((ny, nx))
    u[ele_number*75:(ele_number*75+20), 0] = 1.0  
    u[:, -1] = 0.0  

    max_iter = 100000  
    tolerance = 1e-6  
    for iteration in range(max_iter):
        u_old = u.copy()
        for i in range(1, ny - 1):
            for j in range(1, nx - 1):
                u[i, j] = (u[i+1, j] + u[i-1, j] + u[i, j+1] + u[i, j-1]) / 4
        diff = np.abs(u - u_old).max()
        if diff < tolerance:
            break

    x = np.linspace(xmin, xmax, nx)
    y = np.linspace(ymin, ymax, ny)
    w_potential=ROOT.TGraph2D()
    for i in range(len(y)):
        for j in range(len(x)):
            w_potential.SetPoint(int(i*len(x)+j),x[j]*6,y[i],u[i][j])
    return w_potential

def linearity_w_p(self, depth):
    if depth >= 1:
        w_potential = 1 - (1/(self.l_z-1)) * (depth-1)
    else:
        w_potential = 0
    return w_potential
    