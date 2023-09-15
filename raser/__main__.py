#!/usr/bin/env python3
# Main driver to run raser    
# Author FU Chenxi <1256257282@qq.com>, SHI Xin <shixin@ihep.ac.cn>
# Created [2023-08-29 Tue 11:48] 

import sys 
import argparse
import importlib

VERSION = 4.0

if len(sys.argv) == 1:
    sys.stdout.write('Please use -h for help.\n')
    sys.exit(1)

parser = argparse.ArgumentParser(prog='raser')
parser.add_argument('--version', action='version', 
                    version='%(prog)s {}'.format(VERSION))

subparsers = parser.add_subparsers(help='sub-command help')

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

args = parser.parse_args()


submodules = ['draw', 'field', 'root','spaceres']

submodule = sys.argv[1] 
if submodule not in submodules:
    raise NameError(submodule)

submodule = importlib.import_module(submodule)
submodule.main(args)
