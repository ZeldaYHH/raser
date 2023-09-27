from . import *
def main(args):
    label = vars(args)['label']

    if label == 'foo':
        foo.main()
    else:
        raise NameError(label)