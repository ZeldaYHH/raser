import os
import ROOT

def draw_compare(input_dir, output_dir, label):
    com_name = []
    graphs_i = []
    graphs_c = []

    for file in os.listdir(input_dir):
        if file.endswith('.root'):
            com_name.append(file)

    for name in com_name:
        if label == 'sicar1.1.8' and not name.startswith('sicar1.1.8'):
            continue
        elif label in 'sicar1.1.8-1' and not name.startswith('sicar1.1.8-1_'):
            continue
        elif label in 'sicar1.1.8-2' and not name.startswith('sicar1.1.8-2_'):
            continue
        name = name.split('.root')[0]

        input_file = os.path.join(input_dir, name + '.root')

        if name.endswith('i'):
            file = ROOT.TFile(input_file, "READ")
            tree = file.Get("myTree")
            graph1 = ROOT.TGraph()
            # print(name)
            for i, event in enumerate(tree):
                x = event.Value
                x = abs(x)
                y = event.Reading
                y = abs(y)
                graph1.SetPoint(i, x, y)

            graph1.SetNameTitle("")
            graph1.SetLineWidth(1)
            graph1.SetMarkerColor(ROOT.kBlack)
            graph1.SetMarkerStyle(24)
            graph1.SetMarkerSize(1)

            graph1.GetXaxis().SetTitle("Reverse Bias Voltage [V]")
            graph1.GetXaxis().SetLimits(0,510)
            graph1.GetXaxis().CenterTitle()
            graph1.GetXaxis().SetTitleOffset(1.4)
            graph1.GetXaxis().SetTitleSize(0.05)
            graph1.GetXaxis().SetLabelSize(0.05)
            graph1.GetXaxis().SetNdivisions(505)
            graph1.GetYaxis().SetLimits(1e-11,1e-5)
            graph1.GetYaxis().SetTitle("Current [A]")
            graph1.GetYaxis().CenterTitle()
            graph1.GetYaxis().SetTitleOffset(1.8)
            graph1.GetYaxis().SetTitleSize(0.05)
            graph1.GetYaxis().SetLabelSize(0.05)
            graph1.Draw("AP")

            graphs_i.append(graph1)

        elif name.endswith('c'):
            file = ROOT.TFile(input_file, "READ")
            tree = file.Get("myTree")
            graph2 = ROOT.TGraph()
            for i, event in enumerate(tree):
                x = event.Voltage
                x = abs(x)
                y = event.Capacitance
                y = abs(y)
                graph2.SetPoint(i, x, y)

            graph2.SetNameTitle("")
            graph2.SetLineWidth(1)
            graph2.SetMarkerColor(ROOT.kBlack)
            graph2.SetMarkerStyle(24)
            graph2.SetMarkerSize(1)

            graph2.GetXaxis().SetLimits(0,399.99)
            graph2.GetXaxis().SetTitle("Reverse Bias Voltage [V]")
            graph2.GetXaxis().CenterTitle()
            graph2.GetXaxis().SetTitleOffset(1.4)
            graph2.GetXaxis().SetTitleSize(0.05)
            graph2.GetXaxis().SetLabelSize(0.05)
            graph2.GetXaxis().SetNdivisions(505)
            graph2.GetYaxis().SetLimits(0,1e2)
            graph2.GetYaxis().SetRangeUser(0, 1e2)
            graph2.GetYaxis().SetTitle("Capacitance [pF]")
            graph2.GetYaxis().CenterTitle()
            graph2.GetYaxis().SetTitleOffset(1.8)
            graph2.GetYaxis().SetTitleSize(0.05)
            graph2.GetYaxis().SetLabelSize(0.05)
            graph2.Draw("AP")

            graphs_c.append(graph2) 

    c_i = ROOT.TCanvas("c_i", "c_i", 800, 800)
    c_i.SetLeftMargin(0.22)
    c_i.SetBottomMargin(0.16)
    c_i.SetGrid()
    c_i.SetFrameLineWidth(5)

    legend_i = ROOT.TLegend(0.27,0.67,0.62,0.80)
    legend_i.SetTextSize(0.04)

    c_c = ROOT.TCanvas("c_c", "c_c", 800, 800)
    c_c.SetLeftMargin(0.22)
    c_c.SetBottomMargin(0.16)
    c_c.SetGrid()
    c_c.SetFrameLineWidth(5)

    legend_c = ROOT.TLegend(0.52,0.40,0.87,0.88)
    legend_c.SetTextSize(0.04)

    for i, graph1 in enumerate(graphs_i):
        graph1.Draw()
        legend_i.AddEntry(graph1, com_name[i].split('_')[0])
        # print(com_name[i].split('_')[0])

    legend_i.Draw()

    file_name_i = "comparison_iv.root"
    c_i.SaveAs(os.path.join(output_dir, file_name_i))
    file_name_i = "comparison_iv.pdf"
    c_i.SaveAs(os.path.join(output_dir, file_name_i))
    file_name_i = "comparison_iv.png"
    c_i.SaveAs(os.path.join(output_dir, file_name_i))

    del c_i

    for i, graph2 in enumerate(graphs_c):
        graph2.Draw()
        c_c.SetLogy()
        legend_c.AddEntry(graph2, com_name[i].split('_')[0])

    legend_c.Draw()

    file_name_c = "comparison_cv.root"
    c_c.SaveAs(os.path.join(output_dir, file_name_c))
    file_name_c = "comparison_cv.pdf"
    c_c.SaveAs(os.path.join(output_dir, file_name_c))
    file_name_c = "comparison_cv.png"
    c_c.SaveAs(os.path.join(output_dir, file_name_c))

    del c_c

def main():
    input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
    output_dir = '/afs/ihep.ac.cn/users/w/wangkeqi/raser/output/fig'

    draw_compare(input_dir, output_dir, label)

if __name__ == "__main__":
    main()
