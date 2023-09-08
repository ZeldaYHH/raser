import array
import importlib
import subprocess
import os
import ROOT
import sys
def main(args_dict):
   # print(args_dict)
    if args_dict['option'][0] == 'sicar1.1.8-1':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
    else:
        raise NameError(args_dict)
    # print(input_dir)
    # print(output_dir)
    com_name = 'sicar1.1.8-1_iv'
    input_file = os.path.join(input_dir, com_name + '.csv')
    # output_name = os.path.basename(input_file) + '.root'
    output_file = os.path.join(output_dir, com_name + '.root')
    # print(output_file)
    df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
    df.Snapshot("myTree", output_file, {"Value","Reading"})
    sys.stdout.write('Saved as {}\n%'.format(output_file))


def plot():
    file = ROOT.TFile("test.root" , "READ")
    tree = file.Get("myTree")
    print(tree)
    graph = ROOT.TGraph()
    for i, event in enumerate(tree):
        x = event.Value
        y = event.Reading
        graph.SetPoint(i, -x, y)

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
#   graph.GetYaxis().SetRangeUser(0,100)
#   graph.GetYaxis().SetRangeUser(100,250)
    graph.GetYaxis().SetTitle("Current [A]")
    graph.GetYaxis().CenterTitle()
    graph.GetYaxis().SetTitleOffset(1.8)
    graph.GetYaxis().SetTitleSize(0.05)
    graph.GetYaxis().SetLabelSize(0.05)
    graph.Draw("AP")

    c = ROOT.TCanvas("c","c",500,500)
    c.SetLeftMargin(0.22)
    c.SetBottomMargin(0.16)
    legend = ROOT.TLegend(0.27,0.27,0.62,0.40)
    c.SetGrid()
    c.SetFrameLineWidth(5)

    legend.SetTextSize(0.04)
    legend.AddEntry(graph,"SICAR1.1.8-1")

    c.cd()
    #c.SetLogy()
    graph.Draw()
    legend.Draw()

    c.SaveAs("/scratchfs/bes/wangkeqi/wangkeqi/SICAR1.1.8/SICAR1.1.8-1_iv.pdf")
    c.SaveAs("/scratchfs/bes/wangkeqi/wangkeqi/SICAR1.1.8/SICAR1.1.8-1_iv.root")
# plot()