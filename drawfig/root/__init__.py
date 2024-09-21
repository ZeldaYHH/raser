def main(kwargs):
    from .convert import convert_csv_to_root
    label = kwargs['label']

    if label == 'sicar1.1.8':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8/iv_cv'
    elif label == 'sicar1.1.8-1':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8/iv_cv'
    elif label == 'sicar1.1.8-2':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8/iv_cv'
    elif label == 'itk_md8_data_v1':
        input_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/sensorsimanddata/itkmd8/itkmd8data'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/itkmd8/itkmd8data'
    elif label == 'itk_md8_sim_v1':
        input_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/sensorsimanddata/itkmd8/itkmd8sim'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/itkmd8/itkmd8sim'
    elif label == 'itk_atlas18_sim_v1':
        input_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/sensorsimanddata/itkatlas18/sim'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/atlas18/sim'
    elif label == 'itk_atlas18_data_v1':
        input_dir = '/afs/ihep.ac.cn/users/l/lizhan/disk/scrathfs/sensorsimanddata/itkatlas18/data'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/lizhan/atlas18/data'
    elif label == 'njupin_iv_v1':
        input_dir = "/afs/ihep.ac.cn/users/s/senzhao/njupin"
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/njupin_iv'
    elif label == 'njupin_cv_v1':
        input_dir = "/afs/ihep.ac.cn/users/s/senzhao/njupin/cv"
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/zhaosen/njupin_cv'
    elif label == 'sicar1.1.8_alpha_v1':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8/CCE_1.1.8-8-1/400v'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8/alpha/1/400V'
    elif label == 'sicar1.1.8_beta':
        input_dir = '/scratchfs/bes/wangkeqi/wangkeqi/data/SICAR1.1.8/time_1.1.8-8/20231116/si/beta_'
        output_dir = '/publicfs/atlas/atlasnew/silicondet/itk/raser/wangkeqi/sicar1.1.8/beta'
    else:
        raise NameError(label)

    convert_csv_to_root(input_dir, output_dir, label)

