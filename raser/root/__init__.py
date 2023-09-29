import sys
import os
import ROOT

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
            df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
            if label=="itk_md8_data":
                df.Snapshot("myTree", output_file, {"Voltage_V", "Current_nA"})
            else:
                df.Snapshot("myTree", output_file, {"Value","Reading"})

        if name.endswith('cv'):
            df = ROOT.RDF.MakeCsvDataFrame(input_file, True, ',')
            if label=="itk_md8_sim":
                df.Snapshot("myTree", output_file, {"Voltage", "Capacitance"})
            else:
                df.Snapshot("myTree", output_file, {"Voltage", "Capacitance", "Capacitance^-2"})

        
        sys.stdout.write('Saved as {}\n'.format(output_file))


def main(args):
    label = vars(args)['label']

    if label == 'sicar1.1.8':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
    elif label == 'sicar1.1.8-1':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
    elif label == 'sicar1.1.8-2':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
    elif label == 'itk_md8_data':
        input_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/itkmd8/itkmd8data'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/itkmd8/itkmd8data'
    elif label == 'itk_md8_sim':
        input_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/itkmd8/itkmd8sim'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/itkmd8/itkmd8sim'
    else:
        raise NameError(label)

    convert_csv_to_root(input_dir, output_dir, label)
