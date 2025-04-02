#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@File    :   weighting_potential.py
@Time    :   2025/04/01
@Author  :   Chenxi Fu
@Version :   1.0
'''

import pickle

import numpy as np

from . import devsim_draw
from util.output import create_path

def main(v1, v2, det_name):
    v1 = float(v1)
    v2 = float(v2)
    diff = v2-v1

    v1_potential_file = 'output/field/'+det_name+'/Potential_'+str(v1)+'V.pkl'
    v2_potential_file = 'output/field/'+det_name+'/Potential_'+str(v2)+'V.pkl'
    with open(v1_potential_file,'rb') as file:
        v1_potential = pickle.load(file)
    with open(v2_potential_file,'rb') as file:
        v2_potential = pickle.load(file)
    v1_values = np.array(v1_potential['values'])
    v2_values = np.array(v2_potential['values'])
    points = v1_potential['points']
    dimension = v1_potential['metadata']['dimension']

    values = (v2_values-v1_values)/diff +1
    # +1 forassume v1_ and v2_values obtained from bottom biasing

    w_p_data = {'points': points, 'values': values, 'metadata':{'voltage': 1, 'dimension': dimension}}
    path = 'output/field/'+det_name+'/weightingfield/top/'
    create_path(path)
    w_p_file = path + 'Potential_1V.pkl'
    with open(w_p_file, 'wb') as file:
        pickle.dump(w_p_data, file)

    if dimension == 1:
        devsim_draw.draw1D(points, values, "Weighting Potential", "Depth[um]", "Weighting Potential", 1, path)

    elif dimension == 2:
        x = [point[0] for point in points]
        y = [point[1] for point in points]
        devsim_draw.draw2D(x, y, values, "Weighting Potential", 1, path)

if __name__ == '__main__':
    import sys
    args = sys.argv
    main(args[1], args[2], args[3])