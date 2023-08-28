#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import sys
import subprocess
import os
import diode_common
import json
device="MyDevice"
region="MyRegion"


#分布计算
###
###
###
file_path_Potential ="./output/parainprogram/Potential.pkl"
file_path_Electrons ="./output/parainprogram/Electrons.pkl"
file_path_Holes ="./output/parainprogram/Holes.pkl"


# 使用参数值

# 检查文件是否存在
if not (os.path.exists(file_path_Potential) and os.path.exists(file_path_Electrons) and os.path.exists(file_path_Holes)):
    print("do 0-20")
    params = {
    'bias_v': "0",
    'voltage': "20"
}
    with open('./output/parainprogram/config_loop.json', 'w') as f:
        json.dump(params, f)
    command = [sys.executable, './python/solveCV2D.py']
    process1 = subprocess.Popen(command, stdout=subprocess.PIPE)
    # 实时读取输出
    while True:
        output = process1.stdout.readline().decode().strip()
        if output:
            print(output)
        else:
            break

    process1.wait()
    print("Please run again to get higher voltage")
elif (os.path.exists(file_path_Potential) and os.path.exists(file_path_Electrons) and os.path.exists(file_path_Holes)):
    print("do 20-500")
    voltage = 40
    while voltage < 500:
        params = {
        'bias_v': str(voltage-20),
        'voltage': str(voltage)
                }
        with open('./output/parainprogram/config_loop.json', 'w') as f:
            json.dump(params, f)
        command = [sys.executable, './python/solveCV2D.py']
        process2 = subprocess.Popen(command, stdout=subprocess.PIPE)
        
        while True:
            output = process2.stdout.readline().decode().strip()
            if output:
                print(output)
            else:
                break
        process2.wait()   
        voltage += 20
            
        
            