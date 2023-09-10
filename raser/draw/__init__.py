import os
import ROOT


def draw_figure(input_dir, output_dir):
    com_name = []
    for file in os.listdir(input_dir):
        if file.endswith('.root'):
            com_name.append(file)
    for name in com_name:
        name = name.split('.root')[0]

        input_file = os.path.join(input_dir, name + '.root')
        output_file = os.path.join(output_dir, name + 'v.root')
        pdf_file = os.path.join(output_dir, name + 'v.pdf')
        png_file = os.path.join(output_dir, name + 'v.png')

        if name.endswith('i'):  
            file = ROOT.TFile(input_file, "READ")
            tree = file.Get("myTree")
            graph = ROOT.TGraph()
            for i, event in enumerate(tree):
                x = event.Value
                x = abs(x)
                y = event.Reading
                y = abs(y)
                graph.SetPoint(i, x, y)

            graph.SetNameTitle("")
            graph.SetLineWidth(1)
            graph.SetMarkerColor(ROOT.kBlack)
            graph.SetMarkerStyle(24)
            graph.SetMarkerSize(1)

            graph.GetXaxis().SetTitle("Reverse Bias Voltage [V]")
            graph.GetXaxis().SetLimits(0,510)
            graph.GetXaxis().CenterTitle()
            graph.GetXaxis().SetTitleOffset(1.4)
            graph.GetXaxis().SetTitleSize(0.05)
            graph.GetXaxis().SetLabelSize(0.05)
            graph.GetXaxis().SetNdivisions(505)
            graph.GetYaxis().SetLimits(1e-11,1e-5)
            graph.GetYaxis().SetTitle("Current [A]")
            graph.GetYaxis().CenterTitle()
            graph.GetYaxis().SetTitleOffset(1.8)
            graph.GetYaxis().SetTitleSize(0.05)
            graph.GetYaxis().SetLabelSize(0.05)
            graph.Draw("AP")

            c = ROOT.TCanvas("c","c",500,500)
            c.SetLeftMargin(0.22)
            c.SetBottomMargin(0.16)
            legend = ROOT.TLegend(0.27,0.67,0.62,0.80)
            c.SetGrid()
            c.SetFrameLineWidth(5)

            legend.SetTextSize(0.04)
            legend.AddEntry(graph,name.split('_')[0])

            c.cd()
            graph.Draw()
            legend.Draw()

            c.SaveAs(output_file)
            c.SaveAs(pdf_file)
            c.SaveAs(png_file)
            del c

        if name.endswith('c'):  
            file = ROOT.TFile(input_file, "READ")
            tree = file.Get("myTree")
            graph = ROOT.TGraph()
            for i, event in enumerate(tree):
                x = event.Voltage
                x = abs(x)
                y = event.Capacitance
                y = abs(y)
                graph.SetPoint(i, x, y)

            graph.SetNameTitle("")
            graph.SetLineWidth(1)
            graph.SetMarkerColor(ROOT.kBlack)
            graph.SetMarkerStyle(24)
            graph.SetMarkerSize(1)

            graph.GetXaxis().SetLimits(0,399.99)
            graph.GetXaxis().SetTitle("Reverse Bias Voltage [V]")
            graph.GetXaxis().CenterTitle()
            graph.GetXaxis().SetTitleOffset(1.4)
            graph.GetXaxis().SetTitleSize(0.05)
            graph.GetXaxis().SetLabelSize(0.05)
            graph.GetXaxis().SetNdivisions(505)
            graph.GetYaxis().SetLimits(0,1e2)
            # graph.GetYaxis().SetRangeUser(0,100)
            # graph.GetYaxis().SetRangeUser(100,250)
            graph.GetYaxis().SetTitle("Capacitance [pF]")
            graph.GetYaxis().CenterTitle()
            graph.GetYaxis().SetTitleOffset(1.8)
            graph.GetYaxis().SetTitleSize(0.05)
            graph.GetYaxis().SetLabelSize(0.05)
            graph.Draw("AP")

            c = ROOT.TCanvas("c","c",500,500)
            c.SetLeftMargin(0.22)
            c.SetBottomMargin(0.16)
            legend = ROOT.TLegend(0.52,0.27,0.85,0.40)
            c.SetGrid()
            c.SetFrameLineWidth(5)

            legend.SetTextSize(0.04)
            legend.AddEntry(graph,name.split('_')[0])

            c.cd()
            c.SetLogy()
            graph.Draw()
            legend.Draw()

            c.SaveAs(output_file)
            c.SaveAs(pdf_file)
            c.SaveAs(png_file)
            del c


def main(args):
    label = vars(args)['label']

    if label == 'sicar1.1.8':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
        output_dir = '/afs/ihep.ac.cn/users/w/wangkeqi/raser/output/fig'
    else:
        raise NameError(label)

    draw_figure(input_dir, output_dir)
