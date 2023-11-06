from . import *
def main(args):
    label = vars(args)['label']

    if label == 'foo':
        foo.main()
    if label == 'ngspice_t1':
        import subprocess
        subprocess.run(['ngspice -b -r t1.raw output/T1_tmp.cir'], shell=True)
    else:
        raise NameError(label)