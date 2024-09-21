#!/usr/bin/env python
import ROOT
import csv
import os
from array import array
import numpy as np
from scipy.optimize import curve_fit
# 读取CSV文件
def read_csv(csv_filename):
    data = []
    with open(csv_filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # 跳过表头
        for row in csvreader:
            if csv_filename.endswith("cv.csv"):
                if row:  # 检查是否存在数据
                    x_value = float(row[0]) if row[0] else 0.0
                    y_value = float(row[2]) if row[2] else 0.0
                    data.append((x_value, y_value))
            elif csv_filename.endswith("iv.csv"):
                if row:  # 检查是否存在数据
                    x_value = float(row[0]) if row[0] else 0.0
                    y_value = float(row[1]) if row[1] else 0.0
                    data.append((x_value, y_value))
            elif csv_filename.endswith("other.csv"):
                if row:  # 检查是否存在数据
                    x_value = float(row[0]) if row[0] else 0.0
                    y_value = float(row[1]) if row[1] else 0.0
                    data.append((x_value, y_value))
    
    return data

# 创建ROOT文件并存储数据
def create_root_file(csv_filename, root_filename):
    data = read_csv(csv_filename)

    # 创建ROOT文件
    root_file = ROOT.TFile(root_filename, "RECREATE")

    # 创建TTree对象
    tree = ROOT.TTree("data_tree", "Data from CSV")
    x = ROOT.std.vector('double')()
    y = ROOT.std.vector('double')()
    tree.Branch("x", x)
    tree.Branch("y", y)

    for i, (x_val, y_val) in enumerate(data):
        x.push_back(x_val)
        y.push_back(y_val)
        tree.Fill()

    # 将TTree对象写入ROOT文件
    tree.Write()
    root_file.Close()


def draw_iv_p9():
    # 创建一个Canvas
    c = ROOT.TCanvas('c', '', 800, 600)
    c.SetFillColor(0)
    c.SetFrameFillColor(0)
    ROOT.gStyle.SetPadColor(0)
    ROOT.gStyle.SetCanvasColor(0)
    ROOT.gStyle.SetOptStat(0)
    c.SetLeftMargin(0.15)
    c.SetBottomMargin(0.15)
    c.SetLogy()
    # 遍历文件夹
    folder_path = "/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/samples/"  # 文件夹路径
    colors = [ROOT.kGreen, ROOT.kRed, ROOT.kTeal, ROOT.kYellow, ROOT.kMagenta]  # 定义不同的颜色
    mg=ROOT.TMultiGraph("mg","")
    legend = ROOT.TLegend(0.6, 0.2, 0.8, 0.4) 
    legend.SetBorderSize(0)  # 设置图例的边框大小为0，即没有边框    
    for i,file_name in enumerate(os.listdir(folder_path)):
        if file_name.endswith("iv.root"):  # 如果文件名以"iv.root"结尾
            file_number = int(''.join(filter(str.isdigit, file_name)))
            color_index = file_number - 1 
            root_file = ROOT.TFile(os.path.join(folder_path, file_name))
            tree = root_file.Get("data_tree")  # 获取Tree名称
            n_entries = tree.GetEntries()
            x_data = array('d', [0]*n_entries)  # 创建一个数组来存储x值
            y_data = array('d', [0]*n_entries) 
           
            ex_data = array('d',[0]*n_entries)  # 创建一个数组来存储x误差
            ey_data = array('d',[0]*n_entries)  # 创建一个数组来存储y误差 # 创建一个数组来存储y值
            for n in range(n_entries):
                tree.GetEntry(n)
                for i, x in enumerate(tree.x):
                    if 0 <= abs(x) <= 400:  # 仅添加 0 到 400 之间的 x 值及对应的 y 值
                        x_data.append(abs(x))
                        ex_data.append(0)
                        y_data.append(abs(tree.y[i]/(3.14*0.05*0.05)))
                        ey_data.append(0)
            #print(x_data,y_data)
            #graph = ROOT.TGraphErrors(len(x_data), array('d', x_data), array('d', y_data),ex_data,ey_data)  # 创建TGraph对象
            graph = ROOT.TGraph(len(x_data), array('d', x_data), array('d', y_data))  # 创建TGraph对象
            graph.SetMarkerStyle(20)  # 设置标记形状
            graph.SetMarkerSize(0.5)
            
            graph.SetMarkerColor(colors[color_index])
            mg.Add(graph)  # 添加到TMultiGraph中
            legend.AddEntry(graph, file_name.split("_iv")[0], "p")
       
    
    mg.GetYaxis().SetTitle('Current Density [A/cm^2]')
    mg.GetXaxis().SetTitle('Reverse Bias Voltage [V]')
    mg.GetYaxis().SetLabelSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().CenterTitle(True)  
    mg.GetXaxis().SetLabelSize(0.05)
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetXaxis().CenterTitle(True)  
    mg.SetMinimum(1e-11)  
    mg.SetMaximum(1e-2)  
    mg.Draw('AP')
    legend.Draw()  
    #c.Update()
    
    c.SaveAs("/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/samples/output/iv_comparison.root")
    c.SaveAs("/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/samples/output/iv_comparison.pdf")
    #c.SaveAs("./iv_comparison.root")
    #c.SaveAs("./iv_comparison.pdf")


def draw_cv_p9():
    # 创建一个Canvas
    c = ROOT.TCanvas('c', '', 1200, 600)  # 调整画布大小以容纳两个子图
    #c.Divide(2, 1)  # 将画布分割成两列
    c.SetFillColor(0)
    c.SetFrameFillColor(0)
    ROOT.gStyle.SetPadColor(0)
    ROOT.gStyle.SetCanvasColor(0)
    ROOT.gStyle.SetOptStat(0)
    c.SetLeftMargin(0.15)
    c.SetBottomMargin(0.15)
    c.SetLogy()
    #c.cd(1)
    # 遍历文件夹
    folder_path = "/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/samples"  # 文件夹路径
    mg = ROOT.TMultiGraph("mg", "")
    legend = ROOT.TLegend(0.6, 0.6, 0.8, 0.8)
    legend.SetBorderSize(0)  # 设置图例的边框大小为0，即没有边框    
    colors = [ROOT.kGreen, ROOT.kRed, ROOT.kPink, ROOT.kCyan, ROOT.kOrange]  # 定义不同的颜色
    for i, file_name in enumerate(os.listdir(folder_path)):
        if file_name.endswith("cv.root"):  # 如果文件名以"cv.root"结尾
            file_number = int(''.join(filter(str.isdigit, file_name)))
            color_index = file_number - 1 
            root_file = ROOT.TFile(os.path.join(folder_path, file_name))
            tree = root_file.Get("data_tree")  # 获取Tree名称
            n_entries = tree.GetEntries()
            x_data = array('d', [0] * n_entries)  # 创建一个数组来存储x值
            y_data = array('d', [0] * n_entries)
            ex_data = array('d', [0] * n_entries)  # 创建一个数组来存储x误差
            ey_data = array('d', [0] * n_entries)  # 创建一个数组来存储y误差 # 创建一个数组来存储y值
            for n in range(n_entries):
                tree.GetEntry(n)
                for i, x in enumerate(tree.x):
                    if 0 <= abs(x) <= 400:  # 仅添加 0 到 400 之间的 x 值及对应的 y 值
                        x_data.append(abs(x))
                        ex_data.append(0)
                        y_data.append(abs(tree.y[i]))
                        ey_data.append(0)
            graph = ROOT.TGraph(len(x_data), array('d', x_data), array('d', y_data))  # 创建TGraphErrors对象
            graph.SetMarkerStyle(20)
            graph.SetMarkerColor(colors[color_index])  # 设置标记颜色，使用取余运算重复使用颜色
            #graph.SetLineColor(colors[i % len(colors)]) 
            graph.SetMarkerSize(0.5)
            mg.Add(graph)  # 添加到TMultiGraph中
            
            legend.AddEntry(graph, file_name.split("_cv")[0], "p")
    
    
    mg.GetYaxis().SetTitle('Capacitance [pF]')
    mg.GetXaxis().SetTitle('Reverse Bias Voltage [V]')
    mg.GetYaxis().SetLabelSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().CenterTitle(True)  
    mg.GetXaxis().SetLabelSize(0.05)
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetXaxis().CenterTitle(True)  
    mg.SetMinimum(1e0)
    mg.SetMaximum(1e3)
    mg.Draw('P')
    legend.Draw("same")  
    
    """
    c.cd(2)
    fig2_files="/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/simulation_cv"
    mg=ROOT.TMultiGraph("mg","")
    legend=ROOT.TLegend(0.6,0.6,0.8,0.8)
    legend.SetBorderSize(0)
    for file_name in os.listdir(fig2_files):
        if file_name.endswith("cv_other.root"):  
            root_file = ROOT.TFile(os.path.join(folder_path, file_name))
            tree=root_file.Get("data_tree")
            n_entries=tree.GetEntries()
            x_data = array('d', [0] * n_entries)  # 创建一个数组来存储x值
            y_data = array('d', [0] * n_entries)
            for n in range(n_entries):
                tree.GetEntry(n)
                for i,x in enumerate(tree.x):
                    if 0<x<=400:
                        x_data.append(abs(x))
                        y_data.append(abs(tree.y[i]))
            print(x_data)
            graph=ROOT.TGraph(len(x_data),array("d",x_data),array("d",y_data))
            graph.SetMarkerStyle(20)
            graph.SetMarkerSize(0.5)
            mg.Add(graph)  # 添加到TMultiGraph中
            legend.AddEntry(graph, file_name.split("_cv_other")[0], "p")
        
    mg.GetYaxis().SetTitle('Capacitance [pF]')
    mg.GetXaxis().SetTitle('Reverse Bias Voltage [V]')
    mg.GetYaxis().SetLabelSize(0.05)
    mg.GetYaxis().SetTitleSize(0.05)
    mg.GetYaxis().CenterTitle(True)  
    mg.GetXaxis().SetLabelSize(0.05)
    mg.GetXaxis().SetTitleSize(0.05)
    mg.GetXaxis().CenterTitle(True)  
    mg.SetMinimum(1e0)
    mg.SetMaximum(1e3)
    mg.Draw('P')
    legend.Draw("same")  
    c.Update()"""

    c.SaveAs("/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/samples/output/cv_comparison.root")
    c.SaveAs("/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/samples/output/cv_comparison.pdf")


def main():
    draw_cv_p9()
    draw_iv_p9()
    #test()
    #print("fix cv")