from . import *


def main(args):
    label = vars(args)['label']

    if label == 'temperature':
        from . import calculate_temperature
        calculate_temperature.main()
    else:
        raise NameError(label)