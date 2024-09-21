#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import ROOT
import os
import math
import array
import time as tm
import pandas
def read_file(file_path,wave_name):

    with open(file_path + '/' + wave_name, 'r') as f:
        
        lines = f.readlines()
        points = lines[1:]
        time, volt = [],[]

        for point in points:
            try:
                time.append(float(point.strip('\n').strip().split(',')[3])*1e9)
                volt.append(float(point.strip('\n').strip().split(',')[4])*1e3)
            except Exception as e:
                pass

    return time,volt

def get_max(time_list,volt_list):

    volt_max = 0.
    time_max = 0.
    index_max = 0
    for i in range(len(volt_list)):
        if(volt_list[i]>volt_max):
            time_max = time_list[i]
            volt_max = volt_list[i]
            index_max = i
    return time_max,volt_max,index_max

def get_baseline(time_list,volt_list,time_win):

    time_start = time_list[0]
    time_end = time_start + time_win
    count = 0.
    total = 0.
    for i in range(len(time_list)):
        if(time_list[i] < time_end):
            total += volt_list[i] 
            count += 1.
    baseline = total/count
    return baseline

def get_charge(time_list,volt_list,baseline):

    volt_cut_baseline_list = []
    for i in range(len(volt_list)):
        volt_cut_baseline_list.append(volt_list[i]-baseline)

    time_max,volt_max,index_max = get_max(time_list,volt_cut_baseline_list)

    time_bin = time_list[1]-time_list[0]
    tmp_integrate = 0.
    
    tmp_index = index_max
    while True:
        if(volt_cut_baseline_list[tmp_index]<0.): break
        tmp_integrate += volt_cut_baseline_list[tmp_index]*time_bin
        tmp_index -= 1
    
    tmp_index = index_max+1
    while True:
        if(volt_cut_baseline_list[tmp_index]<0.): break
        tmp_integrate += volt_cut_baseline_list[tmp_index]*time_bin
        tmp_index += 1

    charge = tmp_integrate*(1e-12)/50/100*(1e15)

    return charge



def energy_sim():
    c=ROOT.TCanvas("c","c",700,500)
    charge_graph_file=ROOT.TFile.Open("./output/SiC_LGAD/energy_deposition_final.root")
    charge_graph=charge_graph_file.Get("Edetector")
    
    # 定义新的直方图
    new_hist = ROOT.TH1F("new_histogram", "New Histogram", 200, 4.1, 4.6)
    new_hist.SetStats(0) 
    # 重新填充数据到新的直方图
    for i in range(charge_graph.GetNbinsX()):
        bin_content = charge_graph.GetBinContent(i)
        bin_center = charge_graph.GetBinCenter(i)
        new_hist.Fill(bin_center, bin_content)

    # 将新的直方图保存到文件
    new_file = ROOT.TFile("new_output.root", "RECREATE")
    new_hist.Write()
    new_file.Close()
    npars=3
    f2 = ROOT.TF1("f2", "[2]*TMath::Landau(2*[0]-x, [0], [1])", 4.1, 4.6,npars)
    #f2 = ROOT.TF1("f2", "[2]*TMath::Gaus(x, [0], [1])", 0, 2.5,npars)
    f2.SetParLimits(0,4.,5)
    f2.SetParLimits(1,0,1)
    f2.SetParLimits(2,70.,1000)
    f2.SetParameters(4.4,0.1,70)
    #h=ROOT.TH1F("h","data",75,150,350)
    weight_factor = 1  # 假设增加2倍的权重
    data_file = open("data_points.txt", "w")
    for i in range(new_hist.GetNbinsX()):
        bin_content = new_hist.GetBinContent(i)
        bin_error = new_hist.GetBinError(i)
        #if bin_content < 80:  # 举例：假设高于某个阈值的数据点增加权重
        new_hist.SetBinContent(i, bin_content)
        data_file.write(f"{new_hist.GetXaxis().GetBinCenter(i)} {bin_content}\n")
        new_hist.SetBinError(i,0)
    data_file.close()
    # 进行拟合
    new_hist.Fit(f2,"W") 

    f2.SetLineColor(ROOT.kBlue)
    num_points = 1000  # 设置需要计算的点的数量
    fit_points = []
    for i in range(num_points):
        x = 4 + i * (5 - 4) / num_points  # 在x范围内均匀选取点
        y = f2.Eval(x)  # 计算拟合曲线上的点
        fit_points.append((x, y))

    # 将拟合曲线上的点写入txt文件
    output_file = open("fit_curve.txt", "w")
    for point in fit_points:
        output_file.write(f"{point[0]} {point[1]}\n")

    output_file.close()
    
    new_hist.SetLineColor(ROOT.kBlack)
    new_hist.SetMarkerStyle(20)  # 设置点的样式为实心圆
    new_hist.SetMarkerColor(ROOT.kBlack)  # 设置点的颜色为黑色
    new_hist.SetMinimum(0)  # 设置y轴最小值
    new_hist.SetMaximum(90) 
    new_hist.SetLabelFont(43, "XYZ")
    new_hist.SetTitleFont(43, "XYZ")
    new_hist.SetLabelSize(20, "XYZ")
    new_hist.SetTitleSize(20, "XYZ")
    new_hist.SetLabelSize(0.04, "X")  # 设置X轴标签的长度为2.6
    new_hist.SetLabelSize(0.04, "Y")  # 设置Y轴标签的长度为2.6

    new_hist.Draw("P")
    #f2.Draw("same")
    latex = ROOT.TLatex()
    latex.SetTextSize(0.04)
    latex.SetTextAlign(13)
    latex.DrawLatexNDC(0.2, 0.8, "MPV= %.2f" % (f2.GetParameter(0)))
    #latex.DrawLatexNDC(0.2, 0.6, "sigma= %.2f" % (f2.GetParameter(1)))
    c.SaveAs("./output/SiC_LGAD/fit_alpha.svg")
    c.SaveAs("./output/SiC_LGAD/fit_alpha.root")


def landau_mirror():

    charge_con=[]
    charge_err=[]
    path = '/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/CCE_1.1.8-8-2/'
    c = ROOT.TCanvas('c','c',1500,1200)
    c.SetLeftMargin(0.16)
    c.SetBottomMargin(0.14)
    
    #c.Divide(3, 2) 
    for i, file in enumerate(["100v","150v","200v","250v","300v","350v"]):
        
        input_name = file
        path = '/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/alpha/' + input_name #文件路径
        waves = os.listdir(path)
        time,volt = [],[]
        window = 1

        c.cd(i+1)
        charge = ROOT.RooRealVar("charge", "charge", 30, 200)
        
        charge_graph = ROOT.TH1F('charge','charge',120,30.,200) #bin，最小值，最大值
        # volt_graph = ROOT.TH1F('volt',"volt",50,800,1800)
        xaxis = charge_graph.GetXaxis()
        yaxis = charge_graph.GetYaxis()

        # 设置横轴和纵轴标签
        xaxis.SetTitle("Charge (fC)")
        xaxis.CenterTitle()  # 将标签居中
        xaxis.SetTitleSize(0.04)  # 设置标签的大小


        yaxis.SetTitle("Counts (a.u.)")
        yaxis.CenterTitle()  # 将标签居中
        yaxis.SetTitleSize(0.04)  # 设置标签的大小
        charge_graph.SetStats(0)  # 关闭统计框架S


        output_file_2 = open("charge_histogram.{}txt".format(input_name), "w")
        for wave in waves:
            #print(wave)
            time,volt = read_file(path,wave)
            time_max,volt_max,index_max = get_max(time,volt)
            baseline = get_baseline(time,volt,window)
            try:
                charge = get_charge(time,volt,baseline)
            except:
                print('error')
            if charge > 30 and charge < 330:
                charge_graph.Fill(charge)
                
                output_file_2.write(f"{charge}\n")
        

            charge_var = ROOT.RooRealVar("charge_var", "charge_var", charge)
            data = ROOT.RooDataHist("charge_graph", "charge_graph", ROOT.RooArgList( charge_var), ROOT.RooFit.Import(charge_graph))
        output_file_2.close()
        output_file_2 = open("charge_histogram.{}txt".format(input_name), "w")

        npars=6
        #f2=ROOT.TF1("f2","0.5*[0]*[1]/TMath::Pi() /TMath::Max( 1.e-10,(x-[2])*(x-[2])+ .25*[1]*[1]")
        f2 = ROOT.TF1("f2", "[2]*TMath::Landau(2*[0]-x, [0], [1])+[5]*TMath::Gaus(x,[3],[4])", 30, 200,npars)
        f2.SetParLimits(0,150.,155)
        f2.SetParLimits(1,0.,10)
        f2.SetParLimits(2,0.,1000)
        f2.SetParLimits(3,150.,155)
        f2.SetParLimits(4,0.,10)
        f2.SetParLimits(5,0.,1000)
        f2.SetParameters(150,2,0,150,2,0)
        
        charge_graph.Fit(f2,"w")
        # 计算拟合曲线上的点
        num_points = 1000  # 设置需要计算的点的数量
        fit_points = []
        for i in range(num_points):
            x = 30 + i * (200 - 30) / num_points  # 在x范围内均匀选取点
            y = f2.Eval(x)  # 计算拟合曲线上的点
            fit_points.append((x, y))

        # 将拟合曲线上的点写入txt文件
        output_file = open("fit_curve_points{}.txt".format(input_name), "w")
        for point in fit_points:
            output_file.write(f"{point[0]} {point[1]}\n")

        output_file.close()
        f2.SetLineColor(ROOT.kBlue)

        
        charge_graph.SetLineColor(ROOT.kBlack)
        charge_graph.SetMarkerStyle(20)  # 设置点的样式为实心圆
        charge_graph.SetMarkerColor(ROOT.kBlack)  # 设置点的颜色为黑色
        charge_graph.SetMinimum(0)  # 设置y轴最小值
        charge_graph.SetMaximum(70) 
        graph = ROOT.TGraph()
        graph.GetXaxis().SetLabelFont(42)  # 设置x轴标题的字体
        graph.GetXaxis().SetLabelSize(0.04)  # 设置x轴标题的字号
        graph.GetYaxis().SetLabelFont(42)  # 设置y轴标题的字体
        graph.GetYaxis().SetLabelSize(0.04)
        graph.GetXaxis().SetNdivisions(1010)  # 设置x轴主刻度和次刻度的分割数
        graph.GetYaxis().SetNdivisions(1001)  # 设置y轴主刻度和次刻度的分割数  # 设置y轴标题的字号
        graph.GetXaxis().SetTitle( 'Charge (fC)' )
        graph.GetYaxis().SetTitle( 'Counts (a.u.)' )
        graph.GetXaxis().SetTickLength(0.04)  # 设置x轴刻度长度
        graph.GetYaxis().SetTickLength(0.04)  # 设置y轴刻度长度
        graph.GetXaxis().CenterTitle()  # 将x轴标题居中
        graph.GetYaxis().CenterTitle()  # 将y轴标题居中
        charge_graph.Draw("E")
        #f2.Draw("same")
        latex = ROOT.TLatex()
        latex.SetTextSize(0.04)
        latex.SetTextAlign(13)
        latex.DrawLatexNDC(0.2, 0.8, "MPV= %.2f" % (f2.GetParameter(0)))
        latex.DrawLatexNDC(0.2, 0.7, "SL= %.2f" % (f2.GetParameter(1)))
        #latex.DrawLatexNDC(0.2,0.4,"Charge=%.4f"%(integral_value))
        
       
        charge_con.append(f2.GetParameter(0))
        charge_err.append(f2.GetParameter(1))
   
        c.Update()

        c.SaveAs("fit_alpha" + input_name + ".png")
    canvas=ROOT.TCanvas("canvas","canvas",1500,1200)
    print(charge_con)

    graph=ROOT.TGraphErrors()
    for i,n in enumerate([100,150,200,250,300,350]):
        graph.SetPointError(i,0,charge_err[i])
        graph.SetPoint(i,n,charge_con[i])
    mg=ROOT.TMultiGraph("mg","")
    graph.SetMarkerStyle(20)  # 设置点的样式为实心圆
    graph.SetMarkerColor(ROOT.kBlack)  # 设置点的颜色为黑色
    graph.GetXaxis().SetLabelFont(42)  # 设置x轴标题的字体
    graph.GetXaxis().SetLabelSize(0.04)  # 设置x轴标题的字号
    graph.GetYaxis().SetLabelFont(42)  # 设置y轴标题的字体
    graph.GetYaxis().SetLabelSize(0.04)  # 设置y轴标题的字号
    graph.GetYaxis().SetTitle( 'Charge (fC)' )
    graph.GetXaxis().SetTitle( 'Reverse Bias Voltage (V)' )
    graph.GetXaxis().CenterTitle()  # 将x轴标题居中
    graph.GetYaxis().CenterTitle()  # 将y轴标题居中
    
    graph.Draw("AP")
    data=pandas.read_csv("./raser/draw/fit.csv")
    x = abs(data['X'].values)
    y = abs(data['Y'].values)
    fit_graph=ROOT.TGraph()
    for i ,n in enumerate(x):
        fit_graph.SetPoint(i,n,y[i])
    #fit_graph.SetLineStyle(2)
    fit_graph.SetMarkerStyle(20)  # 设置点的样式为实心圆
    fit_graph.SetMarkerColor(ROOT.kRed)  # 设置点的颜色为黑色
    fit_graph.GetXaxis().SetLabelFont(42)  # 设置x轴标题的字体
    fit_graph.GetXaxis().SetLabelSize(0.04)  # 设置x轴标题的字号
    fit_graph.GetYaxis().SetLabelFont(42)  # 设置y轴标题的字体
    fit_graph.GetYaxis().SetLabelSize(0.04)  # 设置y轴标题的字号
    fit_graph.GetYaxis().SetTitle( 'Charge (fC)' )
    fit_graph.GetXaxis().SetTitle( 'Reverse Bias Voltage (V)' )
    fit_graph.GetXaxis().CenterTitle()  # 将x轴标题居中
    fit_graph.GetYaxis().CenterTitle() 
    fit_graph.Draw("AP")

    mg.Add(graph)
    mg.Add(fit_graph)
    mg.Draw("AP")
    canvas.SaveAs("charge_alpha.root")
    canvas.SaveAs("charge_alpha.png")
            
