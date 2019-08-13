from .dctutils import obsid, crosscorrelation, calib_dir
import astropy.io.fits as pf
import numpy as np
import os
from termcolor import colored

__all__ = ['skyshift']


def skyshift(filenum):
    """Cross correlate the observed sky spectrum with template Lowell_sky.fits"""
    t = pf.open(os.path.join(calib_dir, 'Lowell_sky.fits'))
    sky_f = t[0].data
    sky_w = t[0].header['CRVAL1'] + t[0].header['CD1_1'] * np.arange(len(sky_f))

    fname = obsid(filenum).filename(ext='.ms.fits')
    with pf.open(fname, mode='update') as t:
        hdr = t[0].header
        if 'SKYWAV' not in hdr or hdr['SKYWAV'] != 1:
            i = np.arange(t[0].data.shape[2])
            x_range = hdr['CRVAL1'] + hdr['CD1_1']*i

            #sky spectrum is the third extension
            y = t[0].data[2, 0]
            ind = x_range > 5000
            y_rebinned = np.interp(sky_w, x_range, y)
            delta = (np.argmax(crosscorrelation(sky_f[ind], y_rebinned[ind], 100)) - 100) * t[0].header['CD1_1']
            if delta > 50:
                delta = 0
                print('sky shift failed, no change in wavelength is applied.')

            text = colored("Shifting spectrum by %.2f Angstrom" %(delta, ), 'green')
            print(text)
            hdr['CRVAL1'] += delta
            hdr['SKYWAV'] = 1
