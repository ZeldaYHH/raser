def main(kwargs):    
    label = kwargs['label']
    scan_number = kwargs['scan']
    job_number = kwargs['job']

    if label == 'signal':
        if scan_number != None:
            from util import batchjob
            scan_number = kwargs['scan']
            det_name = kwargs['det_name']
            for i in range(scan_number):
                args = ['signal', '--job', str(i), det_name]
                command = ' '.join(args) 
                print(command)
                destination = 'signal'
                batchjob.main(destination, command, 1, is_test=False)
        elif job_number != None:
            from . import gen_signal_scan
            gen_signal_scan.main(kwargs)
        else:
            from . import gen_signal_main
            gen_signal_main.main(kwargs)