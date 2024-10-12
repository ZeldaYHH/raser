#!/usr/bin/env python3
# Main driver to run raser    
# Author FU Chenxi <1256257282@qq.com>, SHI Xin <shixin@ihep.ac.cn>
# Created [2024-09-21 Sat 16:01] 

import sys 
import argparse
import importlib

VERSION = 4.0

parser = argparse.ArgumentParser(prog='drawfig')
parser.add_argument('--version', action='version', 
                    version='%(prog)s {}'.format(VERSION))
parser.add_argument('-t', '--test', help='TEST', action="store_true")

subparsers = parser.add_subparsers(help='sub-command help', dest="subparser_name")

parser_atlas_itk = subparsers.add_parser('atlas_itk', help='draw atlas itk figures')
parser_atlas_itk.add_argument('label', help='LABEL to identify draw options')

parser_p4 = subparsers.add_parser('p4', help='draw p4 figures')
parser_p4.add_argument('label', help='LABEL to identify draw options')

parser_p9 = subparsers.add_parser('p9', help='draw p9 figures')
# for p9 label is optional
parser_p9.add_argument('-l','--label', help='LABEL to identify draw options')

parser_sicar = subparsers.add_parser('sicar', help='draw sicar figures')
parser_sicar.add_argument('label', help='LABEL to identify draw options')

parser_ucsc = subparsers.add_parser('ucsc', help='draw ucsc figures')
parser_ucsc.add_argument('label', help='LABEL to identify draw options')

parser_root = subparsers.add_parser('root', help='root files conversion')
parser_root.add_argument('label', help='LABEL to identify root files')

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

kwargs = vars(args)

submodules = ['atlas_itk', 'p4', 'p9', 'root', 'sicar', 'ucsc']

submodule = kwargs['subparser_name']
if submodule not in submodules:
    raise NameError(submodule)

submodule = importlib.import_module(submodule)
submodule.main(kwargs)