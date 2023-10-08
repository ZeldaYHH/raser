#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pickle
import numpy as np
import ROOT

class FieldCal:
    def __init__(self, my_d,det_name,det_dic,dev_dic):
        self.voltage = my_d.voltage
        self.l_z = my_d.l_z
        self.read_ele_num = int(dev_dic['read_ele_num'])       
        if(det_name=="Si_Strip"):
            with open("./output/testdiode/x.pkl",'rb') as file:
                x=pickle.load(file)
            with open("./output/testdiode/y.pkl",'rb') as file:
                y=pickle.load(file)
            with open("./output/testdiode/potential_{}.pkl".format(self.voltage),'rb') as file:
                potential=pickle.load(file)
        self.x_efield,self.y_efield,self.potential=get_field(x,y,potential)

        self.w_p=[]
        for i in range(int(self.read_ele_num)):
            self.w_p.append(w_p(i))


    def get_e_field(self, x, y, depth):    
        f_efx = self.x_efield.Interpolate(depth,x)
        f_efz = self.y_efield.Interpolate(depth,x)
        return f_efz, 0, f_efx
    
    def get_w_p(self, x, y, depth, i):
        f_p = self.w_p[i].Interpolate(depth,x)
        return f_p
    
    def get_potential(self, x, y, depth):
        f_u = self.potential.Interpolate(depth,x)
        return f_u
    
def get_field(x,y,potential):
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
    re_potential=ROOT.TGraph2D()
    x_field=ROOT.TGraph2D()
    y_field=ROOT.TGraph2D()
    for i in range(len(x_u)):
        for j in range(len(y_u)):
            x_field.SetPoint(int(i*len(y_u)+j), x_u[i]*1e4, y_u[j]*1e4, x_efield[i][j]/3)
            y_field.SetPoint(int(i*len(y_u)+j), x_u[i]*1e4, y_u[j]*1e4, y_efield[i][j]/3)
            re_potential.SetPoint(int(i*len(y_u)+j), x_u[i]*1e4, y_u[j]*1e4, reorganization_potential[i][j])
    return x_field,y_field,re_potential


def w_p(ele_number):
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

