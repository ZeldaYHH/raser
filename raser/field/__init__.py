import logging
import devsim
from . import gen_devsim_db
from . import scan_cv
from . import devsim_solve
from . import si_diode_1d
from . import si_diode_2d
from . import diode_element_2d
from . import scan_iv
from . import scan_elefield
def main(args):
    label = vars(args)['label']
    verbose = vars(args)['verbose'] 

    if verbose == 1: # -v 
        logging.basicConfig(level=logging.INFO)
    if verbose == 2: # -vv 
        logging.basicConfig(level=logging.DEBUG)

    logging.info('This is INFO messaage')
    logging.debug('This is DEBUG messaage')

    if label == 'gen_devsim_db':
        gen_devsim_db.main()
    elif label == 'sicar1.1.6_cv_v1':
        scan_cv.main(simname="sicar1.1.6")
    elif label == "NJUPIN_cv_v1":
        scan_cv.main(simname="NJUPIN")
    elif label == 'sicar1.1.6_iv_v1':
        scan_iv.main(simname="sicar1.1.6")
    elif label == 'NJUPIN_iv_v1':
        scan_iv.main(simname="NJUPIN")
    elif label == 'NJUPIN_defect_iv_v1':
        scan_iv.main(simname="NJUPIN_defect")
    elif label == 'sicar1.1.8_cv_0-1v':
        devsim_solve.main()
    elif label == 'sicar1.1.8_cv_v1':
        devsim_solve.main(label)
    elif label == 'si_ir_1d':
        si_diode_1d.main()
    elif label == 'si_ir_2d':
        si_diode_2d.main()
    elif label == 'simple_2d_pnjunction_simulate':
        diode_element_2d.main()
    elif label == 'itkmd8_cv_v1':
        devsim_solve.main(label)
    elif label == 'itkmd8_iv_v1':
        devsim_solve.main(label)
    elif label == 'itkatlas18_iv_v1':
        devsim_solve.main(label)
    elif label == "3d_pixel_field":
        scan_elefield.main("3d_pixel")
    elif label == "3d_lgad_cv_v1":
        scan_cv.main("3d_lgad")
    else:
        raise NameError(label)
