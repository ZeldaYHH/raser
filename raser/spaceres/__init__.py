from . import telescope

import sys
sys.path.append("..")
from g4simulation import Particles
from setting import Setting
from geometry import R3dDetector

def main(args):
    label = vars(args)['label']

    if label.startswith("taichu_v1"):
        paths = ['det_name=Taichu3', 'parfile=setting/detector.json', 'geant4_model=pixeldetector', 'geant4_parfile=setting/absorber.json', 'pixeldetector']
        dset = Setting(paths)
        my_d = R3dDetector(dset)
        
        
        my_f = 0
        #my_g4p = Particles(my_d, my_f, dset)
        
        #my_charge = raser.CalCurrentPixel(my_d,my_f,my_g4p, 0)
        #drawsave.draw_charge(my_charge)
        #my_telescope = telescope(my_charge,my_g4p)
        
        telescope.main(args)
    else:
        raise NameError(label)
    