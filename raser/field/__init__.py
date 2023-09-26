import logging
from . import gen_devsim_db
from . import scan_cv
from . import devsim_solve
from . import si_diode_1d
from . import si_diode_2d

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
    elif label == 'sicar1.1.6_cv_0-1v':
        scan_cv.main()
    elif label == 'sicar1.1.8_cv_0-1v':
        devsim_solve.main()
    elif label == 'si_ir_1d':
        si_diode_1d.main()
    elif label == 'si_ir_2d':
        si_diode_2d.main()
    else:
        raise NameError(label)