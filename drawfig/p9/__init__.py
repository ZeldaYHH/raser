import os

from . import draw_iv_cv_paper9
from . import alpha_ana_sicar
from . import data_convolution

def main(kwargs):
    csv_folder="/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/samples"
    for file in os.listdir(csv_folder):
        if file.endswith(".csv"):
            csv_filename = os.path.join(csv_folder, file)
            root_filename = file.replace(".csv", ".root")
            root_fullpath = os.path.join(csv_folder, root_filename)
            draw_iv_cv_paper9.create_root_file(csv_filename, root_fullpath)
    draw_iv_cv_paper9.main()
    alpha_ana_sicar.main()
    data_convolution.landau_mirror()
    data_convolution.energy_sim()