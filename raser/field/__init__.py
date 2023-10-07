import logging
import devsim
from . import gen_devsim_db
from . import scan_cv
from . import devsim_solve

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
    elif label == 'sicar1.1.8_cv_0-400v_1':
        gaindoping = 7.0e16 
        bulkdoping = 2.0e14
        devsim_solve.main(gaindoping,bulkdoping)
    elif label == 'sicar1.1.8_cv_0-400v_2':
        gaindoping = 8.7e16 
        bulkdoping = 3.0e14
        devsim_solve.main(gaindoping,bulkdoping)
    else:
        raise NameError(label)