import sys
import os
import ROOT
import csv

def convert_csv_to_root(input_dir, output_dir, label):
    com_name = []
    for file in os.listdir(input_dir):
        if file.endswith('.csv'):
            com_name.append(file)
    for name in com_name:
        if label == 'sicar1.1.8' and not name.startswith('sicar1.1.8'):
            continue
        elif label == 'sicar1.1.8-1' and not name.startswith('sicar1.1.8-1_'):
            continue
        elif label == 'sicar1.1.8-2' and not name.startswith('sicar1.1.8-2_'):
            continue

        name = name.split('.csv')[0]
        input_file = os.path.join(input_dir, name + '.csv')
        output_file = os.path.join(output_dir, name + '.root')

        if name.endswith('iv'):
            if label=="itk_atlas18_data_v1":
                df = ROOT.RDF.MakeCsvDataFrame(input_file, True, '\t')
            elif label =="njupin_iv_v1":
                df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
            else:
                df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
            if label in ["itk_md8_data_v1","itk_atlas18_data_v1"]:
                df.Snapshot("myTree", output_file, {"Voltage_V", "Current_nA"})
            elif label in ['itk_atlas18_sim_v1','itk_md8_sim_v1']:
                df.Snapshot("myTree", output_file, {"Voltage", "Current"})
            elif label =="njupin_iv_v1":
                df.Snapshot("myTree", output_file, {"Current","Voltage"})
            
            else:
                df.Snapshot("myTree", output_file, {"Value","Reading"})

        if name.endswith('cv'):
            df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
            if label=="itk_md8_sim_v1":
                df.Snapshot("myTree", output_file, {"Voltage", "Capacitance"})
            elif label =="njupin_cv_v1":
                df.Snapshot("myTree", output_file, {"Voltage", "Capacitance"})
            else:
                df.Snapshot("myTree", output_file, {"Voltage", "Capacitance", "Capacitance^-2"})

        if name.endswith('Wfm'):
            df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
            df.Snapshot("myTree", output_file, {"Time", "Volt"})

        
        sys.stdout.write('Saved as {}\n'.format(output_file))
