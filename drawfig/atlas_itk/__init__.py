import os
import ROOT
from . import iv
from . import cv
from . import compare_iv
from . import compare_cv
from . import draw_figure_atlas_itk as dfai


def main(kwargs):
    label = kwargs['label']

    if label == 'sicar1.1.8':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
        output_dir = '/afs/ihep.ac.cn/users/w/wangkeqi/raser/output/fig'
        dfai.draw(input_dir, output_dir, label)
    elif label == 'compare_sicar1.1.8_iv':
        iv.main(label)
    elif label == 'compare_sicar1.1.8_cv':
        cv.main(label)
    elif label == 'sicar1.1.8-1':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
        output_dir = '/afs/ihep.ac.cn/users/w/wangkeqi/raser/output/fig'
        dfai.draw(input_dir, output_dir, label)
    elif label == 'sicar1.1.8-2':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8'
        output_dir = '/afs/ihep.ac.cn/users/w/wangkeqi/raser/output/fig'
        dfai.draw(input_dir, output_dir, label)  
    elif label == 'itk_md8_data_v1':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/itkmd8/itkmd8data'
        output_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/raser/output/fig'
        dfai.draw(input_dir, output_dir, label,xtitle_iv="Reverse Bias Voltage [V]",ytitle_iv="Current [nA]",
                xtitle_cv="Reverse Bias Voltage [V]",ytitle_cv="Capacitance [pF]",
                    xlowerlimit_iv=0,xupperlimit_iv=700,ylowerlimit_iv=1e-11,yupperlimit_iv=1e-5,ylogscale_iv=0,
                    xlowerlimit_cv=0,xupperlimit_cv=400,ylowerlimit_cv=0,yupperlimit_cv=1e2,ylogscale_cv=0)  
    elif label == 'itk_md8_sim_v1':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/itkmd8/itkmd8sim'
        output_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/raser/output/fig'
        dfai.draw(input_dir, output_dir, label,xtitle_iv="Reverse Bias Voltage [V]",ytitle_iv="Current [nA]",
                xtitle_cv="Reverse Bias Voltage [V]",ytitle_cv="Capacitance [pF]",
                    xlowerlimit_iv=0,xupperlimit_iv=700,ylowerlimit_iv=1e-11,yupperlimit_iv=1e-5,ylogscale_iv=0,
                    xlowerlimit_cv=0,xupperlimit_cv=400,ylowerlimit_cv=0,yupperlimit_cv=1e2,ylogscale_cv=0)  
    elif label == 'itk_md8_compare_dataandsim_v1':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/itkmd8/comparison'
        output_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/raser/output/fig'
        cv.main(label)
        iv.main(label)
    elif label == 'itk_atlas18_sim_v1':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/atlas18/sim'
        output_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/raser/output/fig'
        dfai.draw(input_dir, output_dir, label,xtitle_iv="Reverse Bias Voltage [V]",ytitle_iv="Current [A]",
            xtitle_cv="Reverse Bias Voltage [V]",ytitle_cv="Capacitance [pF]",
                xlowerlimit_iv=0,xupperlimit_iv=700,ylowerlimit_iv=1e-11,yupperlimit_iv=1e-5,ylogscale_iv=0,
                xlowerlimit_cv=0,xupperlimit_cv=400,ylowerlimit_cv=0,yupperlimit_cv=1e2,ylogscale_cv=0)
    elif label == 'itk_atlas18_data_v1':
        input_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/atlas18/data'
        output_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/raser/output/fig'
        dfai.draw(input_dir, output_dir, label,xtitle_iv="Reverse Bias Voltage [V]",ytitle_iv="Current [nA]",
                xtitle_cv="Reverse Bias Voltage [V]",ytitle_cv="Capacitance [pF]",
                    xlowerlimit_iv=0,xupperlimit_iv=700,ylowerlimit_iv=1e-11,yupperlimit_iv=1e-5,ylogscale_iv=0,
                    xlowerlimit_cv=0,xupperlimit_cv=400,ylowerlimit_cv=0,yupperlimit_cv=1e2,ylogscale_cv=0) 
    elif label == 'sicar1.1.8-1,sicar1.1.8-2_iv':
        iv.main(label)  
    elif label == 'sicar1.1.8-1,sicar1.1.8-2_cv':
        cv.main(label) 
    elif label == "compare_nju_iv":
        path1="/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/njupin_iv/nju_pin_iv.root"
        path2="./output/2Dresult/simNJUPIN/simIV800.0to800.0.root"
        compare_iv.main(label,path1,path2)
    elif label == "compare_nju_cv":
        path1="/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/njupin_cv/4H-SiC-PIN-cv.root"
        path2="./output/2Dresult/simNJUPIN/simCV500.0to500.0.root"
        compare_cv.main(label,path1,path2)
    elif label == "compare_sim_sicar1.1.8_cv":
        path1="/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8/sicar1.1.8-11_cv.root"
        path2="./output/2Dresult/simsicar1.1.6/simCV500.0to500.0.root"
        compare_cv.main(label,path1,path2)
    elif label == "compare_sicar_cv_1d":
        path1="/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8/iv_cv/sicar1.1.8-8_cv.root"
        path2="./output/field/SICAR-1.1.8/simCV-500.0to0.0.root"
        compare_cv.main(label,path1,path2)
    elif label == "compare_sim_sicar1.1.8_iv":
        path1="/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8/sicar1.1.8-11_iv.root"
        path2="./output/2Dresult/simsicar1.1.6/simIV650.0to650.0.root"
        compare_iv.main(label,path1,path2)
    else: 
        raise NameError(label)
    