from .dctutils import *
from . import cosmics
from .skyshift import skyshift
__all__ = ["extract_ap"]

def extract_ap(filenum, arcobj='CdArNeHg_1.5', extract=True, flux=True,
               telluric_cal_id=None, shift=True, splot="yes", quicklook="no",
               redo='no', resize='yes'): #obj: objects+standard; arcobj: lamps/ comparison frame
    sciobj = obsid(filenum).filename(ext = "")
    if extract:
        obj_proc(sciobj + '.fits')
        iraf.specred()
        fwhm = 5.
        iraf.unlearn('doslit')
        iraf.unlearn('sparams')
        iraf.unlearn('aidpars')

        iraf.doslit.quicklook = quicklook
        iraf.doslit.readnoise = "RON"
        iraf.doslit.gain = "GAIN"
        iraf.doslit.width = 5.
        iraf.doslit.crval = ccdspecs['crval']
        iraf.doslit.cdelt = ccdspecs['CD1_1']
        iraf.sparams.nsum = 50
        iraf.doslit.clean = "yes"
        iraf.doslit.dispaxis = 2
        iraf.sparams.extras = "yes"
        iraf.sparams.lower = -1*int(round(iraf.doslit.width/2.))
        iraf.sparams.upper = int(round(iraf.doslit.width/2.))
        iraf.sparams.t_function = "legendre"
        iraf.sparams.t_niter = 3
        iraf.sparams.t_order = 4
        iraf.sparams.t_high = 2
        iraf.sparams.t_low = 2
        iraf.sparams.weights = "variance"
        iraf.sparams.b_order = 3
        iraf.sparams.b_niterate = 1
        iraf.sparams.select = "average"
        anullus_start = fwhm*2
        xL = np.floor(np.linspace(-80, -1*anullus_start, 10))
        xR = np.floor(np.linspace(anullus_start, 80, 10))
        background_range = ''
        for i in np.arange(xL.size-1):
            background_range += '%d:%d,' % (np.int(xL[i]), np.int(xL[i+1]-1))
        for i in np.arange(xR.size-1):
            background_range += '%d:%d,' % (np.int(xR[i]+1), np.int(xR[i+1]))
        iraf.sparams.b_sample = background_range[:-1]
        iraf.sparams.i_function = "legendre"
        iraf.sparams.i_order = 7
        iraf.sparams.coordlist = "linelists$DCTline.dat"
        iraf.sparams.fwidth = ccdspecs['fwhm_arc']
        iraf.sparams.match = 10. # positive number is angstrom, negative is pix
        iraf.sparams.i_niterate = 5
        iraf.sparams.addfeatures = 'no'
        iraf.sparams.linearize = "yes"

        iraf.doslit(sciobj + ".fits", arcs=arcobj + ".fits", splot=splot, redo=redo, resize=resize)

        #Setting air mass of the observation
        iraf.setairmass.images = sciobj+'.ms'
        iraf.setairmass.equinox = "equinox"
        iraf.setairmass.st = "lst-obs"
        iraf.setairmass.ut = "ut"
        iraf.setairmass.exposure = "exptime"
        iraf.setairmass.airmass = "airmass"
        iraf.setairmass()
    if shift:
        skyshift(filenum)
    if telluric_cal_id is not None:
        telluric(sciobj, telluric_cal_id)
    if flux:
        iraf.unlearn('calibrate')
        # mode switch to make the input noninteractive
        iraf.calibrate.mode = 'h'
        iraf.calibrate.input = sciobj+'.ms'
        iraf.calibrate.output = sciobj+'_flux'
        iraf.calibrate.extinction = 'onedstds$kpnoextinct.dat'
        iraf.calibrate.sensitivity = 'sens.0001'
        iraf.calibrate.ignoreaps = 'yes'
        iraf.calibrate()
        move_files([sciobj+'.fits'])

def obj_proc(files,trace=None):
    if trace is None:
        trace = ccdspecs['trace']
    iraf.unlearn('ccdproc')
    iraf.ccdproc.zerocor = "no"
    iraf.ccdproc.darkcor = "no"
    iraf.ccdproc.flatcor = 'yes'
    iraf.ccdproc.fixpix = "no"
    iraf.ccdproc.biassec = ccdspecs['BIASSEC']
    iraf.ccdproc.trimsec = "[%d:%d,*]" % (trace-100, trace+100)
    iraf.ccdproc.function = "legendre"
    iraf.ccdproc.order = 1
    iraf.ccdproc.ccdtype = ""
    iraf.ccdproc.niterate = 3
    if isinstance(files, str):
        files = [files]
    for filename in files:
        iraf.hedit(filename, 'GAIN', ccdspecs['gain'], add="yes",
            update="yes", verify="no", show="no")
        iraf.hedit(filename, 'RON', ccdspecs['readnoise'], add="yes",
            update="yes", verify="no", show="no")
        iraf.ccdproc(filename, flat="flat_1.5.fits")

        array, header = pf.getdata(filename, header=True)
        if 'COSMIC' not in header or header['COSMIC'] != 1:
            c = cosmics.cosmicsimage(array, gain=ccdspecs['gain'],
                readnoise=ccdspecs['readnoise'],
                sigclip = 4.5, sigfrac = 0.5, objlim = 2.0, satlevel=60000,
                skyOrder = 0, objectOrder = 0)
            c.run(maxiter = 3)
            header.set('COSMIC', 1, '1 if we ran LA Cosmic')
            pf.writeto(filename, c.cleanarray, header, clobber=True)
