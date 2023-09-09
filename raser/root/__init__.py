# from .__main__ import main
import sys
import os
import ROOT

def convert_cvs_to_root(input_dir, output_dir):
    com_name = []
    for file in os.listdir(input_dir):
        if file.endswith('.csv'):
            com_name.append(file)
    for name in com_name:
        name = name.split('.csv')[0]
        input_file = os.path.join(input_dir, name + '.csv')
        output_file = os.path.join(output_dir, name.split('v')[0] + '.root')

        if name.endswith('iv'):
            df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
            df.Snapshot("myTree", output_file, {"Value","Reading"})

        if name.endswith('cv'):
            df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
            df.Snapshot("myTree", output_file, {"Voltage", "Capacitance", "Capacitance^-2"})
        
        sys.stdout.write('Saved as {}\n'.format(output_file))


def main(args):
    label = vars(args)['label']

    if label == 'sicar1.1.8':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
    else:
        raise NameError(label)

    convert_cvs_to_root(input_dir, output_dir)
