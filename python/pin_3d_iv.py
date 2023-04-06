import devsim 
import os
import sys
sys.path.append("..")

import math
from array import array

from sicar import Physics
from sicar import Node
from sicar import Initial


import csv

import matplotlib.pyplot as plt
import pin_3d_mesh

if not (os.path.exists("./output")):
    os.mkdir("./output")

if not (os.path.exists("./output/reverse")):
    os.mkdir("./output/reverse")

device="3d_pin"
region="3d_pin"


area_factor = 25e4


pin_3d_mesh.Create3DSICARFromGmesh(device=device, region=region)
pin_3d_mesh.SetDoping(device=device, region=region)
pin_3d_mesh.Draw_Doping(device=device, region=region, path="./output/3d_pin_doping.png")

devsim.open_db(filename="../sicar/SICARDB", permission="readonly")

# Extended precision
devsim.set_parameter(name = "extended_solver", value=True)
devsim.set_parameter(name = "extended_model", value=True)
devsim.set_parameter(name = "extended_equation", value=True)

# For converge
devsim.set_parameter(name = "n_i", value=6.7e10)


### Drift diffusion simulation at equilibrium
Initial.InitialSolution(device, region)
Initial.DriftDiffusionInitialSolution(device, region)
devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)

#### Ramp the bias to Reverse
reverse_v = 0.0
reverse_voltage = []
reverse_top_current = []
reverse_bot_current = []
reverse_bulk_current = []
n = 0

reverse_voltage.append(0.)
reverse_top_current.append(0.)

f = open("./output/pin_3d_mesh.csv", "w")
header = ["Voltage","Current"]
writer = csv.writer(f)
writer.writerow(header)

#devsim.delete_node_model(device=device, region=region, name="IntrinsicElectrons")
#devsim.delete_node_model(device=device, region=region, name="IntrinsicHoles")
while reverse_v < 2000:
    
    
    devsim.set_parameter(device=device, name=Physics.GetContactBiasName("top"), value=0-reverse_v)
    devsim.solve(type="dc", absolute_error=1e10, relative_error=1e-10, maximum_iterations=30)
    Physics.PrintCurrents(device, "top")
    Physics.PrintCurrents(device, "bot")
    reverse_bulk_electron_current= devsim.get_contact_current(device=device, contact="top", equation="ElectronContinuityEquation")
    reverse_bulk_hole_current    = devsim.get_contact_current(device=device, contact="top", equation="HoleContinuityEquation")
    reverse_bulk_total_current   = reverse_bulk_electron_current + reverse_bulk_hole_current       
    reverse_voltage.append(0-reverse_v)
    reverse_bulk_current.append(abs(reverse_bulk_total_current))
    writer.writerow([0-reverse_v,abs(reverse_bulk_total_current/area_factor)])

    #if(reverse_v%10==0):
    devsim.write_devices (file="./output/reverse/pin_3d_mesh_reverse_bias_%s.dat"%(str(n)), type="tecplot")
    
    
    reverse_v += 1  
    n += 1
    
    

f.close()
devsim.close_db()

print(reverse_voltage)
print(reverse_bulk_current)

#fig3=matplotlib.pyplot.figure(num=3,figsize=(4,4))
#matplotlib.pyplot.semilogy(reverse_voltage, reverse_bulk_current)
#matplotlib.pyplot.xlabel('Voltage (V)')
#matplotlib.pyplot.ylabel('Current (A)')
   #matplotlib.pyplot.axis([min(reverse_voltage), max(reverse_voltage), 1e-9, 1e-2])
#matplotlib.pyplot.savefig("./output/3d_sicar_iv.png")



exampleReader = csv.reader("./output/pin_3d_mesh_iv.csv")  # 读取csv文件
exampleData = list(exampleReader)  # csv数据转换为列表
length_zu = len(exampleData)  # 得到数据行数
length_yuan = len(exampleData[0])  # 得到每行长度

# for i in range(1,length_zu):
#     print(exampleData[i])

x = list()
y = list()

for i in range(1, length_zu):  # 从第二行开始读取
    x.append(exampleData[i][0])  # 将第一列数据从第二行读取到最后一行赋给列表x
    y.append(exampleData[i][1])  # 将第二列数据从第二行读取到最后一行赋给列表

plt.plot(x, y)  # 绘制x,y的折线图
plt.show()  # 显示折线图

