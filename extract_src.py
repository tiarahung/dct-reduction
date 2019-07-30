#! /usr/local/miniconda2/envs/iraf27/bin/python
from dctpipeline.dctutils import *
from dctpipeline.extract_ap import *
from dctpipeline.skyshift import *
from dctpipeline.telluric_remove import *
from dctpipeline.sensfunc import *

#mkbstar('20190629.0048.ms.fits')
#skyshift('0063')

#extract_ap('0063', extract=True, flux=False, shift=True, telluric=False)
#sensfunc(['0063'])
#mkbstar('20190629.0063.ms.fits')

obsgroup = ['0064', '0065']
for num in obsgroup:
	extract_ap(num, extract=True, flux=True, shift=True, telluric=True)

coadd(obsgroup)

#telluric_remove('20190629.0049.ms.fits', 'bstar.fits')
