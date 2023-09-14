from . import gen_devsim_db
from . import scan_cv
def main(args):
    label = vars(args)['label']
    batch= vars(args)['batch']
    print(batch)
    exit()
   

    if label == 'gen_devsim_db':
        gen_devsim_db.main()
    if label == 'sicar1.1.6_cv_0-1v':
        scan_cv.main(batch=batch)
    else:
        raise NameError(label)