from .dctutils import obsid, pf, np

__all__ = ['skyshift']


def skyshift(filenum):
    """Cross correlate the observed sky spectrum with template Lowell_sky.fits"""
    t = pf.open('Lowell_sky.fits')
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
            y_rebinned = np.interp(sky_w, x_range, y)
            delta = (np.argmax(crosscorrelation(sky_f, y_rebinned, 200)) - 200) * t[0].header['CD1_1']
            print("Shifting spectrum by %.2f Angstrom" %(delta, ))
            hdr['CRVAL1'] += delta
            hdr['SKYWAV'] = 1

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
