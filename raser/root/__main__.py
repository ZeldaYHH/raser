import os
import ROOT
import sys
def main(args_dict):
    if args_dict['option'][0] == 'sicar1.1.8-1':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
    else:
        raise NameError(args_dict)
    com_name = 'sicar1.1.8-1_iv'
    input_file = os.path.join(input_dir, com_name + '.csv')
    output_file = os.path.join(output_dir, com_name + '.root')
    df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
    df.Snapshot("myTree", output_file, {"Value","Reading"})
    sys.stdout.write('Saved as {}\n%'.format(output_file))
