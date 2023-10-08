from . import *
def main(args):
    label = vars(args)['label']
    if label == 'temperature':
        from . import cal_temp
        cal_temp.main()
    else:
        raise NameError(label)