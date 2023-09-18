import logging
from . import gen_devsim_db


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
    if label == 'sicar1.1.6_cv_0-1v':
        scan_cv.main(batch=batch)
    else:
        raise NameError(label)