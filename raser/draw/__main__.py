import os
import ROOT

def main(args_dict):
    if args_dict['option'][1] == 'sicar1.1.8-1':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
        output_dir = '/afs/ihep.ac.cn/users/w/wangkeqi/raser/output/fig'
    else:
        raise NameError(args_dict)
    com_name = 'sicar1.1.8-1_iv'
    input_file = os.path.join(input_dir, com_name + '.root')
    output_file = os.path.join(output_dir, com_name + '.root')
    pdf_file = os.path.join(output_dir, com_name + '.pdf')
    png_file = os.path.join(output_dir, com_name + '.png')

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
    legend.AddEntry(graph,"SICAR1.1.8-1")

    c.cd()
    graph.Draw()
    legend.Draw()

    c.SaveAs(output_file)
    c.SaveAs(pdf_file)
    c.SaveAs(png_file)