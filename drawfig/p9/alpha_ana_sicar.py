import ROOT
import os
import numpy
import sys
import math

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

def main():
    path = '/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/CCE_1.1.8-8-2/'
    for file in ["100V","150V","200V","250V","300V","350V"]:
        input_name = file
        path = '/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/CCE_1.1.8-8-2/' + input_name #文件路径
        waves = os.listdir(path)
        time,volt = [],[]
        window = 1

        c = ROOT.TCanvas('c','c',600,500)
        c.SetLeftMargin(0.16)
        c.SetBottomMargin(0.14)
        # c = ROOT.TCanvas('c','c',1500,600)
        # c.Divide(2,1)
        charge_graph = ROOT.TH1F('charge','charge',50,150,350) #bin，最小值，最大值
        # volt_graph = ROOT.TH1F('volt',"volt",50,800,1800)
        charge_graph.SetStats(0)  # 关闭统计框架
        # volt_graph.SetStats(0)    # 关闭统计框架


        for wave in waves:

            print(wave)
            time,volt = read_file(path,wave)
            time_max,volt_max,index_max = get_max(time,volt)
            baseline = get_baseline(time,volt,window)
            try:
                charge = get_charge(time,volt,baseline)
            except:
                print('error')
            if charge > 30 and charge < 330:
                charge_graph.Fill(charge)
                # volt_graph.Fill(volt_max)
            
            charge_graph.SetTitle(' ')
            charge_graph.GetXaxis().SetTitle("Charge (fC)")
            charge_graph.GetXaxis().CenterTitle()
            charge_graph.GetXaxis().SetTitleOffset(1.2)
            charge_graph.GetXaxis().SetTitleSize(0.05)
            charge_graph.GetXaxis().SetLabelSize(0.05)
            # charge_graph.GetXaxis().SetNdivisions(505)
            charge_graph.GetYaxis().CenterTitle()
            charge_graph.GetYaxis().SetTitleOffset(1.6)
            charge_graph.GetYaxis().SetTitleSize(0.05)
            charge_graph.GetYaxis().SetLabelSize(0.05)
            # ROOT.TGaxis.SetMaxDigits(3)
            # charge_graph.GetYaxis().SetMaxDigits(3)
            # charge_graph.GetYaxis().SetRangeUser(79, 104.99)
            
            # volt_graph.GetXaxis().SetTitle('Voltage [mV]')

            # c.cd(1)
            c.cd()
            charge_graph.Draw()
            
            gaussian = ROOT.TF1("gaussian", "gaus", 150, 350)
            
            
            charge_graph.Fit(gaussian, "R")
            #gaussian.Draw("same")

            mean = gaussian.GetParameter(1)
            sigma = gaussian.GetParameter(2)
            # 添加朗道分布
            
            landau = ROOT.TF1("landau", "landau", 150, 350)  # 创建朗道分布函数
            charge_graph.Fit(landau,"R")
            #landau.Draw("same")
            
            
            landau_mean = landau.GetParameter(0)
            landau_sigma = landau.GetParameter(1)
            
            convolution = ROOT.TF1("convolution", "landau*gaus", 150, 350)  # 创建卷积函数
            convolution.SetParameters(landau_mean, landau_sigma, mean, sigma)  # 设置初始参数
            charge_graph.Fit(convolution, "R")  # 进行卷积拟合
            x_max = convolution.GetMaximumX()
            #convolution.GetParameter()
            convolution.Draw("same")
            latex = ROOT.TLatex()
            latex.SetTextSize(0.04)
            latex.SetTextAlign(13)
            latex.DrawLatexNDC(0.2, 0.8, "x_max = %.2f" % x_max )
            # latex.DrawLatexNDC(0.2, 0.75, "Sigma = %.2f" % sigma)

            # c.cd(2)
            # volt_graph.Draw()

            c.SaveAs('/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/CCE_1.1.8-8-2/fig_sen/'+ input_name + '_distribution_cut.png')
            c.SaveAs('/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/CCE_1.1.8-8-2/fig_sen/'+ input_name + '_distribution_cut.pdf')
if __name__ == '__main__':
    main()