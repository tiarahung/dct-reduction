from dctpipeline.dctutils import *
from dctpipeline.extract_ap import *
from dctpipeline.sensfunc import *
from dctpipeline.telluric_remove import *
import argparse, os, shutil

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description='Extract a flux standard and fit the sensitivity function')
	parser.add_argument('-f', '--filenum', action='store', nargs='+', dest='filenum',
                    help='file number of the star to be extracted (e.g. 0036)')
	parser.add_argument('-m', action='store_true', dest='mkbstar', default=False,
                    help='Make normalized spectrum for telluric correction')
	args = parser.parse_args()
	k = 0
	for fnum in args.filenum:
		if os.path.isfile(obsid(fnum).filename(ext='.fits')):
			extract_ap(fnum, extract=True, flux=False, shift=True, telluric=False)
			k += 1
		else:
			print('Invalid file number. File %s does not exist' %(obsid(args.filenum).filename(ext='.fits'),))
	if k > 0:
		sensfunc(args.filenum)
		if args.mkbstar:
			mkbstar(obsid(fnum).filename(ext='.ms.fits'))
		else:
			shutil.copy(os.path.join(calib_dir, 'bstar.fits'), '.')

