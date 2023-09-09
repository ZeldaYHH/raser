#!/usr/bin/env python3
# Main driver to run raser    
# Author FU Chenxi <1256257282@qq.com>, SHI Xin <shixin@ihep.ac.cn>
# Created [2023-08-29 Tue 11:48] 

import sys 
import argparse
import importlib


if len(sys.argv) == 1:
    sys.stdout.write('Please use -h for help.\n')
    sys.exit(1)


submodules = ['root']

submodule = sys.argv[1] 
if submodule not in submodules:
    raise NameError(submodule)

parser = argparse.ArgumentParser(prog='raser')
subparsers = parser.add_subparsers(help='sub-command help')

parser_root = subparsers.add_parser('root', help='root files conversion')
parser_root.add_argument('label', help='LABEL to identify root files')


args = parser.parse_args()
submodule = importlib.import_module(submodule)
submodule.main(args)
