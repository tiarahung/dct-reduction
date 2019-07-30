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
calib_dir = os.path.abspath(os.path.dirname(__file__))
calib_dir = os.path.join(calib_dir, 'misc')


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

def getwave(fitsfile):
    with pf.open(fitsfile) as t:
        hdr = t[0].header
        wave = hdr['CRVAL1'] + np.arange(hdr['NAXIS1'])*hdr['CD1_1']
    return wave

def interp(wav, flux, wnew):
    from scipy import interpolate
    f = interpolate.interp1d(wav, flux)
    return f(wnew)

def box_smooth(arr,n=2):
    arr = np.array(arr)
    q = 1
    c = arr[:-n+1]
    p = -n+2
    while p < 0:
        c = c + arr[q:p]
        q += 1
        p += 1
    c = c + arr[q:]
    return c[::n] / float(n)

def crosscorrelation(x, y, maxlag):
    """
    https://stackoverflow.com/questions/30677241/how-to-limit-cross-correlation-window-width-in-numpy?rq=1
    User Warren Weckesser
    https://stackoverflow.com/users/1217358/warren-weckesser
    Cross correlation with a maximum number of lags.
    `x` and `y` must be one-dimensional numpy arrays with the same length.
    This computes the same result as
        numpy.correlate(x, y, mode='full')[len(a)-maxlag-1:len(a)+maxlag]
    The return vaue has length 2*maxlag + 1.
    np.argmax of the return correlation vector gives the value to add to y
    np.argmax-maxlag
    """
    import numpy as np
    from numpy.lib.stride_tricks import as_strided
    # need to normalize here so that spectra with wildly different fluxes will
    # correlate properly (zero-normalized cross correlation)
    xx = (x-np.mean(x))/np.std(x)
    yy = (y-np.mean(y))/np.std(y)/len(y)
    py = np.pad(yy.conj(), 2*maxlag, mode='constant')
    T = as_strided(py[2*maxlag:], shape=(2*maxlag+1, len(yy) + 2*maxlag),
                   strides=(-py.strides[0], py.strides[0]))
    px = np.pad(xx, maxlag, mode='constant')
    return T.dot(px)


def coadd(spectra):
    spec_file = obsid(spectra[0]).filename(ext = '_flux.fits')
    t = pf.open(spec_file)
    exptime = 0.0

    spec = np.zeros([t[0].header['NAXIS1'],len(spectra)])
    err = np.zeros([t[0].header['NAXIS1'],len(spectra)])
    rawbg_fit = np.zeros([t[0].header['NAXIS1'],len(spectra)])
    bg_fit = np.zeros([t[0].header['NAXIS1'],len(spectra)])

    tarname = t[0].header['SCITARG']

    spec[:,0] = t[0].data[0,0,:]
    rawbg_fit[:,0] = t[0].data[1,0,:]
    bg_fit[:,0] = t[0].data[2,0,:]
    err[:,0] = t[0].data[3,0,:]

    exptime += t[0].header['EXPTIME']

    t.close()
    i = 1
    for specname in spectra[1:]:
        spec_file = obsid(specname).filename(ext = '_flux.fits')
        u = pf.open(spec_file)
        spec[:,i] = u[0].data[0,0,:]
        rawbg_fit[:,i] = u[0].data[1,0,:]
        bg_fit[:,i] = u[0].data[2,0,:]
        err[:,i] = u[0].data[3,0,:]
        exptime += u[0].header['EXPTIME']
        u.close()
        i += 1
    rawbg_avg, sum_weights = np.average(rawbg_fit,weights = 1./err**2, axis=1, returned = True)
    bg_avg, sum_weights = np.average(bg_fit,weights = 1./err**2, axis=1, returned = True)
    spec_avg, sum_weights = np.average(spec,weights = 1./err**2, axis=1, returned = True)
    err_avg = 1./np.sqrt(sum_weights)
    arr = np.dstack([spec_avg,rawbg_avg,bg_avg,err_avg])
    arr = np.rollaxis(arr,2)
    f = pf.HDUList([pf.PrimaryHDU(arr)])
    f[0].header = t[0].header
    f[0].header['EXPTIME'] = exptime
    f.writeto(tarname+'_flux.fits')



class obsid:
    def __init__(self, num):
        self.num = num
        fitsfiles = glob.glob('[0-9]'*8+'.'+'[0-9]'*4 + '.fits')
        self.date = fitsfiles[0][:8]
    def filename(self, ext='fits'):
        return "%s.%s%s" %(self.date, self.num, ext)
