import os
import subprocess
from util.output import output

def main(kwargs):
    label = kwargs['label'] # Operation label or detector name
    name = kwargs['name'] # readout electronics name
    os.makedirs('output/elec/{}'.format(name), exist_ok=True)

    if label == 'trans':
        subprocess.run(['ngspice -b setting/electronics/{}.cir'.format(name)], shell=True)
    elif label == 'readout':
        from . import readout
        readout.main(name)
    elif label == 'batch_signal':
        from . import recreate_batch_signals
        recreate_batch_signals.main(name, kwargs['source'])
    else:
        raise NameError

