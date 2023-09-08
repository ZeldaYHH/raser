import os
import ROOT
import sys

def main(args_dict):
    if args_dict['option'][0] == 'sicar1.1.8':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
    else:
        raise NameError(args_dict)
    
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
            df.Snapshot("myTree", output_file, {"Bias Voltage", "Measured Capacitance", "Capacitance^-2"})
        
        sys.stdout.write('Saved as {}\n'.format(output_file))
