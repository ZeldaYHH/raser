#!/usr/bin/env python3
# Main driver to run raser    
# Author FU Chenxi <1256257282@qq.com>, SHI Xin <shixin@ihep.ac.cn>
# Created [2023-08-29 Tue 11:48] 

import sys 
import argparse
import importlib
import subprocess

VERSION = 4.0

parser = argparse.ArgumentParser(prog='raser')
parser.add_argument('--version', action='version', 
                    version='%(prog)s {}'.format(VERSION))
parser.add_argument('-b', '--batch', help='submit BATCH job to cluster', action="store_true")
parser.add_argument('-t', '--test', help='TEST', action="store_true")

subparsers = parser.add_subparsers(help='sub-command help', dest="subparser_name")

parser_draw = subparsers.add_parser('draw', help='draw figures')
parser_draw.add_argument('label', help='LABEL to identify root files')

parser_field = subparsers.add_parser('field', help='calculate field and iv/cv')
parser_field.add_argument('label', help='LABEL to identify operation')
parser_field.add_argument('-v', '--verbose', help='VERBOSE level', 
                          action='count', default=0)

<<<<<<< HEAD
=======
parser_field.add_argument("-b","--batch", help="run in batch mode",action="store_true")

>>>>>>> raser/main
parser_root = subparsers.add_parser('root', help='root files conversion')
parser_root.add_argument('label', help='LABEL to identify root files')

parser_spaceres = subparsers.add_parser('spaceres', help='spaceres calculation')
parser_spaceres.add_argument('label', help='LABEL to identify spaceres files')

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

submodules = ['draw', 'field', 'root', 'spaceres']

submodule = vars(args)['subparser_name']
if submodule not in submodules:
    raise NameError(submodule)

if vars(args)['batch'] == True:
    batchjob = importlib.import_module('batchjob')
    destination = submodule
    command = ' '.join(sys.argv[1:])
    print('batch command: {}'.format(command))
    command = command.replace('--batch ', '')
    command = command.replace('-b ', '')
    batchjob.main(destination, command, args)
else:
    submodule = importlib.import_module(submodule)
    submodule.main(args)
