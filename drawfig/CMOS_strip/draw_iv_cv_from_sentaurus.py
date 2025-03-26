#!/usr/bin/env python3

import os
import csv

import ROOT
ROOT.gROOT.SetBatch(True)

# ROOT do not allow to adjust minimum value of X axis
# in 6.32 a warning is added but it still not work

# Use Data -> Export XY Data in SVisual to obtain .csv file from Sentaurus

path = "/afs/ihep.ac.cn/users/f/fuchenxi/disk/workfs2/sentaurus/2025-04-single_strip"
areafactor = 20000

def draw(name, func_x=float, func_y=float, y_title="", tag=""):
    # 初始化数据容器
    x_values = []
    y_values = []
    # 读取CSV文件（假设第一行为标题行）
    with open(name+'.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            try:
                x_values.append(func_x(row[0]))
                y_values.append(func_y(row[1]))
            except (ValueError, TypeError, IndexError):
                continue

    # 创建ROOT TGraph
    n_points = len(x_values)
    graph = ROOT.TGraph(n_points)

    # 填充数据点
    for i in range(n_points):
        graph.SetPoint(i, x_values[i], y_values[i])

    # 设置图形属性
    graph.SetTitle(name+";Reverse Bias Voltage [V];"+y_title)  # 标题和坐标轴标签
    graph.SetLineColor(ROOT.kBlack)    # 线条颜色（蓝色）
    graph.SetLineWidth(2)            # 线宽

    # 创建画布
    canvas = ROOT.TCanvas("canvas", name, 800, 600)

     # 设置坐标轴范围并绘制
    graph.GetXaxis().SetRangeUser(max(x_values)*-0.05, max(x_values)*1.05)
    graph.GetYaxis().SetRangeUser(0, max(y_values)*1.05)
    graph.Draw("AL")  # A:绘制坐标轴，P:绘制数据点，L:绘制连线

    # 更新画布并保持显示
    canvas.Update()
    canvas.SaveAs(name+tag+".png")  # 保存为图片文件

def func_v(v):
    return float(v)*-1 # 反向偏压
def func_i(i):
    return float(i)*areafactor
def func_c(c):
    return float(c)*areafactor
def func_1_c_2(c):
    return 1/(float(c)*areafactor)**2 

draw(os.path.join(path, "iv_2k_150um"), func_x=func_v, func_y=func_i, y_title="Current [A]")
draw(os.path.join(path, "iv_4k_150um"), func_x=func_v, func_y=func_i, y_title="Current [A]")
draw(os.path.join(path, "cv_2k_150um"), func_x=func_v, func_y=func_c, y_title="Capacitance [F]")
draw(os.path.join(path, "cv_4k_150um"), func_x=func_v, func_y=func_c, y_title="Capacitance [F]")
draw(os.path.join(path, "cv_2k_150um"), func_x=func_v, func_y=func_1_c_2, y_title="1/C^2 [1/(F)^2]", tag="_1_c_2")
draw(os.path.join(path, "cv_4k_150um"), func_x=func_v, func_y=func_1_c_2, y_title="1/C^2 [1/(F)^2]", tag="_1_c_2")