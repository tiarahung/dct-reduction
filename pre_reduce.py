from dctpipeline.dctutils import *
import shutil, glob

def updateheader():
    iraf.hedit('*.fits', 'DISPAXIS', 1, update='yes', verify='no', add='yes', show='no')


def makeobjlist():
    fitsfiles = glob.glob('[0-9]'*8+'.'+'[0-9]'*4+'.fits')
    bias,flat,science_obj,lamp=[],[],[],[]
    objlist = []
    with open('objlist.txt', 'w') as f:
        f.write('#FILENAME          TYPE         TARGET          EXPTIME GRATING  DATE \n')
        for x in sorted(fitsfiles):
            with pf.open(x) as t:
                hdr = t[0].header
                f.write('%s %s %s %s %s %s\n' %(x, hdr['OBSTYPE'].ljust(12), hdr['SCITARG'].ljust(15),
                                                str(int(hdr['EXPTIME'])).ljust(7), hdr['GRATING'], hdr['DATE']))


def subtract_overscan(files):
    """Subtract overscan from all frames then trim each image."""
    iraf.ccdproc.zerocor = "no"
    iraf.ccdproc.flatcor = "no"
    iraf.ccdproc.fixpix = "no"
    iraf.ccdproc.overscan = "yes"
    iraf.ccdproc.biassec = ccdspecs['BIASSEC']
    iraf.ccdproc.trimsec = ccdspecs['TRIMSEC']
    iraf.ccdproc.function = "legendre"
    iraf.ccdproc.order = 1
    iraf.ccdproc.darkcor = "no"
    iraf.ccdproc.ccdtype = ""
    iraf.ccdproc.niterate = 3
    for f in files:
        iraf.ccdproc(f)


def make_response(flatfiles):
    iraf.flatcombine.ccdtype = ""
    iraf.flatcombine.process = "no"
    iraf.flatcombine.subsets = "no"
    iraf.flatcombine.rdnoise = "RDNOISE"
    iraf.flatcombine.gain = "GAIN"
    iraf.flatcombine(','.join(flatfiles), output='masterflat.fits', reject='avsigclip')
    iraf.response.function = "spline3"
    iraf.response.order = 100
    iraf.response.niterate = 3
    iraf.response.low_rej = 3
    iraf.response.high_rej = 3
    iraf.response.interactive = "no"
    iraf.response('masterflat.fits', 'masterflat.fits', 'flat_1.5.fits', interactive="yes")
    for flat in flatfiles:
        os.remove(flat)

def make_arc(arcfiles):
    iraf.unlearn('imcombine')
    iraf.imcombine.rdnoise = ccdspecs['readnoise']
    iraf.imcombine.gain = ccdspecs['gain']
    iraf.imcombine(','.join(arcfiles), 'CdArNeHg_1.5', reject="none")
    #move files to raw dir
    for arc in arcfiles:
        os.remove(arc)

if __name__ == '__main__':
    pwd= os.getcwd()
    rawdir=pwd+"/raw/"
    if not os.path.isdir(rawdir):
        os.mkdir(rawdir)
    for f in glob.glob('*.fits'):
        shutil.copy(f, rawdir)
    updateheader()
    makeobjlist()
    Bias,Flat,Obj,Arc = loadobjects()
    assert (len(Arc) < 10), 'You have more than 10 arc files, does that seem right? Remove focus loop products before proceeding.'
    for bias in Bias:
        os.remove(bias)
    subtract_overscan(Flat)
    subtract_overscan(Obj)
    subtract_overscan(Arc)
    make_response(Flat)
    make_arc(Arc)
