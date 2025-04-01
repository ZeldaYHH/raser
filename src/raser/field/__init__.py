import logging

def main(kwargs):
    label = kwargs['label']
    verbose = kwargs['verbose'] 
    is_umf = kwargs['umf']

    if verbose == 1: # -v 
        logging.basicConfig(level=logging.INFO)
    if verbose == 2: # -vv 
        logging.basicConfig(level=logging.DEBUG)

    logging.info('This is INFO messaage')
    logging.debug('This is DEBUG messaage')

    if is_umf is not True:
        from . import solver_section
        solver_section.main(kwargs)
    else:
        import subprocess
        import sys
        args = sys.argv[1:]
        args.remove('-umf')
        command_tail = " ".join(args)
        command_head = "python3 -mdevsim.umfpack.umfshim src/raser/__main__.py"
        command = command_head + " " + command_tail
        subprocess.run([command], shell=True)
