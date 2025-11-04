#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@File    :   devsim_field.py
@Time    :   2023/06/04
@Author  :   Henry Stone, Sen Zhao
@Version :   2.0
'''

import pickle
import re
import os

import ROOT
ROOT.gROOT.SetBatch(True)
import numpy as np

from ..util.math import *

verbose = 0

class DevsimField:
    def __init__(self, device_name, dimension, voltage, read_out_contact, irradiation_flux = 0):
        self.name = device_name
        self.voltage = voltage
        self.dimension = dimension
        self.read_out_contact = read_out_contact
        # need to be consistent to the detector json

        path = "./output/field/{}/".format(self.name)

        # Weighting Potential is universal for all irradiation flux
        # TODO: Net Doping should be here too
        WeightingPotentialFiles = []
        for contact in read_out_contact:
            WeightingPotentialFiles.append(path + "weightingfield/{}/Potential_{}V.pkl".format(contact['name'], 1))

        if irradiation_flux != 0:
            path = "./output/field/{}/{}/".format(self.name, irradiation_flux)

        doping_file_pattern = re.compile(r'^NetDoping_(-?\d+\.?\d*)V\.pkl$')
        for filename in os.listdir(path):
            if doping_file_pattern.match(filename):
                DopingFile = path + filename
                # example: DopingFile = path + "NetDoping_0V.pkl"
                break

        PotentialFile = path + "Potential_{}V.pkl".format(self.voltage)
        TrappingRate_pFile = path + "TrappingRate_p_{}V.pkl".format(self.voltage)
        TrappingRate_nFile = path + "TrappingRate_n_{}V.pkl".format(self.voltage)

        self.set_doping(DopingFile) #self.Doping
        self.set_potential(PotentialFile) #self.Potential, self.x_efield, self.y_efield, self.z_efield
        self.set_trap_p(TrappingRate_pFile) # self.TrappingRate_p
        self.set_trap_n(TrappingRate_nFile) # self.TrappingRate_n
        self.set_w_p(WeightingPotentialFiles) #self.weighting_potential[]

    def set_doping(self, DopingFile):
        try:
            with open(DopingFile,'rb') as file:
                DopingNotUniform=pickle.load(file)
                print("Doping file loaded for {}".format(self.name))
                if DopingNotUniform['metadata']['dimension'] < self.dimension:
                    print("Doping dimension not match")
                    return
        except FileNotFoundError:
            print("Doping file not found at {}, please run field simulation first".format(DopingFile))
            print("or manually set the doping file")
            return
        
        if DopingNotUniform['metadata']['dimension'] == 1:
            DopingUniform = get_common_interpolate_1d(DopingNotUniform)
        elif DopingNotUniform['metadata']['dimension'] == 2:
            DopingUniform = get_common_interpolate_2d(DopingNotUniform)
        elif DopingNotUniform['metadata']['dimension'] == 3:
            DopingUniform = get_common_interpolate_3d(DopingNotUniform)

        self.Doping = DopingUniform

    def set_potential(self, PotentialFile):
        try:
            with open(PotentialFile,'rb') as file:
                PotentialNotUniform=pickle.load(file)
                print("Potential file loaded for {}".format(self.name))
                if PotentialNotUniform['metadata']['dimension'] < self.dimension:
                    print("Potential dimension not match")
                    return
        except FileNotFoundError:
            print("Potential file not found at {}, please run field simulation first".format(PotentialFile))
            print("or manually set the potential file")
            return
        
        if PotentialNotUniform['metadata']['dimension'] == 1:
            PotentialUniform = get_common_interpolate_1d(PotentialNotUniform)
        elif PotentialNotUniform['metadata']['dimension'] == 2:
            PotentialUniform = get_common_interpolate_2d(PotentialNotUniform)
        elif PotentialNotUniform['metadata']['dimension'] == 3:
            PotentialUniform = get_common_interpolate_3d(PotentialNotUniform)

        self.Potential = PotentialUniform


    def set_w_p(self,WeightingPotentialFiles):
        self.WeightingPotential = []
        for i in range(len(self.read_out_contact)):
            WeightingPotentialFile = WeightingPotentialFiles[i]
            try:
                with open(WeightingPotentialFile,'rb') as file:
                    WeightingPotentialNotUniform=pickle.load(file)
                    print("Weighting Potential file loaded for {} at electrode {}".format(self.name, i+1))
                    if WeightingPotentialNotUniform['metadata']['dimension'] < self.dimension:
                        print("Weighting Potential dimension not match")
                        return
            except FileNotFoundError:
                print("Weighting Potential file not found at {}, please run field simulation first".format(WeightingPotentialFile))
                print("or manually set the Weighting Potential file")
                return
            
            if WeightingPotentialNotUniform['metadata']['dimension'] == 1:
                WeightingPotentialUniform = get_common_interpolate_1d(WeightingPotentialNotUniform)
            elif WeightingPotentialNotUniform['metadata']['dimension'] == 2:
                WeightingPotentialUniform = get_common_interpolate_2d(WeightingPotentialNotUniform)
            elif WeightingPotentialNotUniform['metadata']['dimension'] == 3:
                WeightingPotentialUniform = get_common_interpolate_3d(WeightingPotentialNotUniform)

            self.WeightingPotential.append(WeightingPotentialUniform)
    
    def set_trap_p(self, TrappingRate_pFile):
        try:
            with open(TrappingRate_pFile,'rb') as file:
                TrappingRate_pNotUniform=pickle.load(file)
                print("TrappingRate_p file loaded for {}".format(self.name))
                if TrappingRate_pNotUniform['metadata']['dimension'] < self.dimension:
                    print("TrappingRate_p dimension not match")
                    return
        except FileNotFoundError:
            print("TrappingRate_p file not found at {}, please run field simulation first".format(TrappingRate_pFile))
            print("or manually set the hole trapping rate file")
            return
        
        if TrappingRate_pNotUniform['metadata']['dimension'] == 1:
            TrappingRate_pUniform = get_common_interpolate_1d(TrappingRate_pNotUniform)
        elif TrappingRate_pNotUniform['metadata']['dimension'] == 2:
            TrappingRate_pUniform = get_common_interpolate_2d(TrappingRate_pNotUniform)
        elif TrappingRate_pNotUniform['metadata']['dimension'] == 3:
            TrappingRate_pUniform = get_common_interpolate_3d(TrappingRate_pNotUniform)

        self.TrappingRate_p = TrappingRate_pUniform
    
    def set_trap_n(self, TrappingRate_nFile):
        try:
            with open(TrappingRate_nFile,'rb') as file:
                TrappingRate_nNotUniform=pickle.load(file)
                print("TrappingRate_n file loaded for {}".format(self.name))
                if TrappingRate_nNotUniform['metadata']['dimension'] != self.dimension:
                    print("TrappingRate_n dimension not match")
                    return
        except FileNotFoundError:
            print("TrappingRate_n file not found at {}, please run field simulation first".format(TrappingRate_nFile))
            print("or manually set the electron trapping rate file")
            return
        
        if TrappingRate_nNotUniform['metadata']['dimension'] == 1:
            TrappingRate_nUniform = get_common_interpolate_1d(TrappingRate_nNotUniform)
        elif TrappingRate_nNotUniform['metadata']['dimension'] == 2:
            TrappingRate_nUniform = get_common_interpolate_2d(TrappingRate_nNotUniform)
        elif TrappingRate_nNotUniform['metadata']['dimension'] == 3:
            TrappingRate_nUniform = get_common_interpolate_3d(TrappingRate_nNotUniform)

        self.TrappingRate_n = TrappingRate_nUniform
        

    # DEVSIM dimension order: x, y, z
    # RASER dimension order: z, x, y

    def get_doping(self, x, y, z):
        '''
            input: position in um
            output: doping in cm^-3
        '''
        x, y, z = x/1e4, y/1e4, z/1e4 # um to cm
        if self.dimension == 1:
            return self.Doping(z)
        elif self.dimension == 2:
            return self.Doping(z, x)
        elif self.dimension == 3:
            return self.Doping(z, x, y)
    
    def get_potential(self, x, y, z):
        '''
            input: position in um
            output: potential in V
        '''
        x, y, z = x/1e4, y/1e4, z/1e4 # um to cm
        if self.dimension == 1:
            return self.Potential(z)
        elif self.dimension == 2:
            return self.Potential(z, x)
        elif self.dimension == 3:
            return self.Potential(z, x, y)
    
    def get_e_field(self, x, y, z):
        '''
            input: position in um
            output: intensity in V/um
        ''' 
        x, y, z = x / 1e4, y / 1e4, z / 1e4  # um to cm

        if self.dimension == 1:
            nabla_U = calculate_gradient(self.Potential, ['z'], [z])
            E_z = -1 * nabla_U[0]
            return (0, 0, E_z)

        elif self.dimension == 2:
            nabla_U = calculate_gradient(self.Potential, ['z', 'x'], [z, x])
            E_z = -1 * nabla_U[0]
            E_x = -1 * nabla_U[1]
            return (E_x, 0, E_z)

        elif self.dimension == 3:
            nabla_U = calculate_gradient(self.Potential, ['z', 'x', 'y'], [z, x, y])
            E_z = -1 * nabla_U[0]
            E_x = -1 * nabla_U[1]
            E_y = -1 * nabla_U[2]
            return (E_x, E_y, E_z)

    def get_w_p(self, x, y, z, i): # used in cal current
        x, y, z = x/1e4, y/1e4, z/1e4 # um to cm
        if self.dimension == 1:
            U_w = self.WeightingPotential[i](z)
        elif self.dimension == 2:
            U_w = self.WeightingPotential[i](z, x)
        elif self.dimension == 3:
            U_w = self.WeightingPotential[i](z, x, y)

        # exclude non-physical values
        if U_w < 0:
            if verbose > 0:
                print('U_w is negative at',x*1e4,y*1e4,z*1e4,i,'as',U_w)
            return 0
        elif U_w > 1:
            if verbose > 0:
                print('U_w is greater than 1 at',x*1e4,y*1e4,z*1e4,i,'as',U_w)
            return 1
        elif U_w != U_w:
            if verbose > 0:
                print('U_w is nan at',x*1e4,y*1e4,z*1e4,i)
            return 0
        else:
            return U_w

    
    def get_trap_e(self, x, y, z):
        '''
            input: position in um
            output: electron trapping rate in s^-1     
        '''
        x, y, z = x/1e4, y/1e4, z/1e4 # um to cm
        if self.dimension == 1:
            return self.TrappingRate_n(z)
        
        elif self.dimension == 2:
            return self.TrappingRate_n(z, x)
        
        elif self.dimension == 3:
            return self.TrappingRate_n(z, x, y)
    
    def get_trap_h(self, x, y, z):
        '''
            input: position in um
            output: hole trapping rate in s^-1     
        '''
        x, y, z = x/1e4, y/1e4, z/1e4 # um to cm
        if self.dimension == 1:
            return self.TrappingRate_p(z)
        elif self.dimension == 2:
            return self.TrappingRate_p(z, x)
        elif self.dimension == 3:
            return self.TrappingRate_p(z, x, y)


if __name__ == "__main__":
    pass