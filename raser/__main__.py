#!/usr/bin/env python3
# Main driver to run raser    
# Author FU Chenxi <1256257282@qq.com>, SHI Xin <shixin@ihep.ac.cn>
# Created [2023-08-29 Tue 11:48] 

import sys 
import argparse
import importlib
import subprocess

VERSION = 4.1

parser = argparse.ArgumentParser(prog='raser')
parser.add_argument('--version', action='version', 
                    version='%(prog)s {}'.format(VERSION))
parser.add_argument('-b', '--batch', help='submit BATCH job to cluster', action="store_true")
parser.add_argument('-t', '--test', help='TEST', action="store_true")
parser.add_argument('-sh', '--shell', help='flag of run raser in SHELL', action="store_true")

subparsers = parser.add_subparsers(help='sub-command help', dest="subparser_name")

parser_draw = subparsers.add_parser('draw', help='draw figures')
parser_draw.add_argument('label', help='LABEL to identify root files')

parser_field = subparsers.add_parser('field', help='calculate field and iv/cv')
parser_field.add_argument('label', help='LABEL to identify operation')
parser_field.add_argument('-v', '--verbose', help='VERBOSE level', 
                          action='count', default=0)

parser_root = subparsers.add_parser('root', help='root files conversion')
parser_root.add_argument('label', help='LABEL to identify root files')

parser_spaceres = subparsers.add_parser('spaceres', help='spaceres calculation')
parser_spaceres.add_argument('label', help='LABEL to identify spaceres files')

parser_gen_signal = subparsers.add_parser('gen_signal', help='generate signal')
parser_gen_signal.add_argument('label', nargs='*', help='LABEL to identify spaceres files')

parser_gsignal = subparsers.add_parser('particle', help='calculate particle')
parser_gsignal.add_argument('label', help='LABEL to identify spaceres files')

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

submodules = ['draw', 'field', 'root', 'spaceres', 'gen_signal','particle']

submodule = vars(args)['subparser_name']
if submodule not in submodules:
    raise NameError(submodule)

if vars(args)['batch'] == True:
    batchjob = importlib.import_module('batchjob')
    destination = submodule
    command = ' '.join(sys.argv[1:])
    command = command.replace('--batch ', '')
    command = command.replace('-b ', '')
    print('batch command: {}'.format(command))
    batchjob.main(destination, command, args)
elif vars(args)['shell'] == False: # not in shell
    command = ' '.join(['-sh']+sys.argv[1:])
    import os
    IMGFILE = os.environ.get('IMGFILE')
    BINDPATH = os.environ.get('BINDPATH')
    raser_shell = "/usr/bin/apptainer exec --env-file cfg/env -B" + " " \
                + BINDPATH + " " \
                + IMGFILE + " " \
                + "python3 raser"
    print('shell command: {}'.format(command))
    subprocess.run([raser_shell+' '+command], shell=True, executable='/bin/bash')
else: # in shell
    submodule = importlib.import_module(submodule)
    if submodule.__name__ == "gen_signal":
        submodule.main(vars(args)['label'])
    else:
        submodule.main(args)
