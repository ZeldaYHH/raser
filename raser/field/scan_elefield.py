#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import sys
import subprocess
import os
import json


def main(simname):
    
    device="MyDevice"
    region="MyRegion"
    # 指定文件夹路径
    folder_path = "./output/parainprogram"

    # 检查文件夹是否存在，如果不存在则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    #分布计算
    ###
    ###
    ###
    file_path_Potential ="./output/parainprogram/Potential.pkl"
    file_path_Electrons ="./output/parainprogram/Electrons.pkl"
    file_path_Holes ="./output/parainprogram/Holes.pkl"


    # 使用参数值

    # 检查文件是否存在
    #改变voltage之后可以实现不同的电压上限
    if not (os.path.exists(file_path_Potential) and os.path.exists(file_path_Electrons) and os.path.exists(file_path_Holes)):
        print("do 0-5")
        params = {
        'bias_v': "0",
        'voltage': "5"
    }
        with open('./output/parainprogram/config_loop_elefield.json', 'w') as f:
            json.dump(params, f)
        command = [sys.executable, './raser/field/loop_elefield.py',simname]
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


        #DONOT CHANGE THIS PLS
    elif (os.path.exists(file_path_Potential) and os.path.exists(file_path_Electrons) and os.path.exists(file_path_Holes)):
        print("do 2-500")
        voltage = 2
        while voltage < 200:
            params = {
            'bias_v': str(voltage-1),
            'voltage': str(voltage)
                    }
            with open('./output/parainprogram/config_loopiv.json', 'w') as f:
                json.dump(params, f)
            command = [sys.executable, './raser/field/loop_iv.py']
            process2 = subprocess.Popen(command, stdout=subprocess.PIPE)
            
            while True:
                output = process2.stdout.readline().decode().strip()
                if output:
                    print(output)
                else:
                    break
            process2.wait()   
            
            voltage += 1
                
            
if __name__ == "__main__":
    main(simname)               