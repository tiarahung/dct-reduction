#! /usr/local/miniconda2/envs/iraf27/bin/python
from dctpipeline.dctutils import *
from dctpipeline.extract_ap import *
import argparse, os



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract and flux calibrate a science target. Frames supplied are combined into a single spectrum')
    parser.add_argument('-f', '--filenum', action='store', nargs='+', dest='filenum',
                help='file number(s) to be extracted (e.g. 0036 0037)')
    args = parser.parse_args()
    obsgroup = args.filenum
    for num in obsgroup:
        extract_ap(num, extract=True, flux=True, shift=True, telluric=True)

    coadd(obsgroup)
