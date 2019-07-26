import sys
import os
import re
import numpy as np
from pyraf import iraf
import astropy.io.fits as pf
import matplotlib.pyplot as plt
import glob

iraf.noao(_doprint = 0)
iraf.imred(_doprint = 0)
iraf.ccdred(_doprint = 0)
iraf.kpnoslit(_doprint=0)
iraf.astutil(_doprint=0)
iraf.onedspec(_doprint=0)
iraf.reset(imextn="fxf:fits,FITS")
ccdspecs = {'central_lam': 5800,
			'gain': 1.52,
			'readnoise': 4.9,
			'trace': 280,
            'crval': 3530,
            'CD1_1': 2.18,
            'arc': 'CdArNeHg_1.5.fits',
            'fwhm_arc': 2.7*1.5,
            'pixel_size': 15.,
            'BIASSEC': '[2101:2144,5:512]',
            'TRIMSEC': '[54:2096,5:512]'}
def loadobjects():
	if os.path.isfile('objlist.txt'):
		A = np.genfromtxt('objlist.txt', usecols=(0, 1), dtype='str')
		return A[A[:,1] == 'BIAS', 0], A[A[:,1] == 'DOME', 0], A[A[:,1] == 'OBJECT', 0], A[A[:,1] == 'COMPARISON', 0]
	else:
		print("objlist.txt has not been generated. Run pre_reduced first")

def move_files(filelist):
    for file in filelist:
        if os.path.isfile(file):
            os.rename(file,"raw/"+file)

class obsid:
	def __init__(self, num):
		self.num = num
		fitsfiles = glob.glob('[0-9]'*8+'.'+'[0-9]'*4 + '.fits')
		self.date = fitsfiles[0][:8]
	def filename(self, ext='fits'):
		return "%s.%s%s" %(self.date, self.num, ext)
