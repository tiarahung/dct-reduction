import astropy.io.fits as pf
import numpy as np
import os
from .dctutils import box_smooth, interp, crosscorrelation, getwave
from scipy.interpolate import splrep,splev
import matplotlib.pyplot as plt


__all__ = ['mkbstar', 'telluric_remove']

def mkbstar(starspec):
    """Normalize the star and get the telluric spectrum"""
    wav = getwave(starspec)
    t = pf.open(starspec)
    flux = t[0].data[0, 0]
    #Fit a continuum to the binned spectrum (averaged every 20 pixels)
    n_pixels = 20
    binned_wav, binned_flux = box_smooth(wav, n_pixels), box_smooth(flux, n_pixels)

    # Masking known telluric + Halpha features
    def mask_lines(wl):
        mask = ((wl >= 5600) & (wl <= 6050)) + ((wl >= 6250) & (wl <= 6360))
        mask += ((wl >= 6450) & (wl <= 6530)) + ((wl >= 6500) & (wl <= 6650))
        mask += ((wl >= 6840) & (wl <= 7400)) + ((wl >= 7500) & (wl <= 7750))
        return mask

    mask = mask_lines(binned_wav)
    splfit_mask = (binned_wav > 5500) * ~mask
    spl = splrep(binned_wav[splfit_mask], binned_flux[splfit_mask])
    x2 = wav[wav > 5500]
    y2 = splev(x2, spl)
    fig, ax = plt.subplots(1, figsize=(7, 3))
    ax.plot(wav, flux, 'b', lw=0.7)
    ax.plot(x2, y2, color='C3', lw=1.0)
    mask_wav = mask_lines(wav)
    ax.plot(wav[mask_wav], flux[mask_wav], color='C1', lw=0.7)
    plt.savefig('star_continuum_fit.png')
    plt.close()
    norm_telluric = np.ones(len(flux))
    norm_telluric[wav > 5500] = flux[wav > 5500] / y2

    filename = 'bstar.fits'
    file_exist = os.path.isfile(filename)
    filename_appendix = 1
    while file_exist is True:
        filename = 'bstar.%s.fits' %(str(filename_appendix).rjust(4, '0'))
        file_exist = os.path.isfile(filename)
        filename_appendix += 1
    pf.writeto(filename, norm_telluric, header=t[0].header)
    print('Saved the normalized telluric spectrum to %s' %(filename,))
    return filename

def telluric_remove(scispec, telluric_spec):
    import copy
    """Removing telluric features from science spectrum before flux calibration."""
    t = pf.open(telluric_spec)
    wav_bstar = getwave(telluric_spec)
    flux_bstar = t[0].data

    u = pf.open(scispec)
    wav_obj = getwave(scispec)
    flux_obj = u[0].data[0, 0]
    hdr = u[0].header

    bstar_interp = interp(wav_bstar, flux_bstar, wav_obj)

    Aband = (wav_obj > 7500) & (wav_obj < 7800)
    maxlag = 100
    xcorr = np.argmax(crosscorrelation(flux_obj[Aband], bstar_interp[Aband], maxlag))
    bstar_interp = np.roll(flux_bstar, (xcorr - maxlag)) ** ((u[0].header['AIRMASS'] / t[0].header['AIRMASS']))

    fitsdata = copy.deepcopy(u[0].data)

    fitsdata[0, 0] = flux_obj / bstar_interp
    fitsdata[3, 0] = fitsdata[3, 0] / bstar_interp

    hdr['TELLURIC'] = 1
    filename = 't' + scispec
    pf.writeto(filename, fitsdata, header=hdr)

    t.close()
    u.close()

    fig, ax = plt.subplots(1, figsize=(7, 3))
    ax.plot(wav_obj, flux_obj, label='original', lw=0.7)
    ax.plot(wav_obj, flux_obj / bstar_interp, label='after telluric removal', lw=0.7)
    ax.legend()
    plt.close()


