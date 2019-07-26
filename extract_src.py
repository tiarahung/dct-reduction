#! /usr/local/miniconda2/envs/iraf27/bin/python
from dctpipeline.dctutils import *
from dctpipeline.extract import *
from dctpipeline.skyshift import *

skyshift('0048')
#extract_ap('0049', extract=True, flux=False, shift=False)
