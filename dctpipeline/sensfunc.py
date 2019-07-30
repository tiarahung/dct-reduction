from .dctutils import *
from .extract_ap import *

__all__ = ['sensfunc']

def sensfunc(star_list, extract=True, caldir = "onedstds$spec50cal/", splot='yes'):
    """
    Extract (telluric) flux standard star spectrum for correction in flux.
    Create a sensitivity function.
    star_list should be in list format e.g. ['0011', '0012']
    """
    redo = 'no'
    if extract:
        for i, imgID in enumerate(star_list):
            extract_ap(imgID, arcobj='CdArNeHg_1.5', splot=splot, telluric=False,
                redo=redo, resize='yes', flux=False, quicklook = 'no')

    #No clobber
    if os.path.isfile('std'):
        iraf.delete('std', verify='no')
    if os.path.isfile('sens.0001.fits'):
        iraf.delete('sens.0001.fits', verify='no')

    iraf.unlearn('standard')
    iraf.standard.caldir = caldir
    iraf.standard.output = 'std'
    # use the tabulated bandpasses for the standards
    iraf.standard.bandwidth = "INDEF"
    iraf.standard.bandsep = "INDEF"
    iraf.standard.extinction = 'onedstds$kpnoextinct.dat'
    iraf.standard.observatory = 'lowell'
    # try these one at a time

    star_list_ms = [obsid(num).filename(ext = '.ms.fits') for num in star_list]

    iraf.standard(','.join(star_list_ms))

    iraf.unlearn('sensfunc')
    iraf.sensfunc.standards = 'std'
    iraf.sensfunc.sensitivity = 'sens'
    iraf.sensfunc.extinction = 'onedstds$kpnoextinct.dat'

    iraf.sensfunc.order = 6
    iraf.sensfunc()
