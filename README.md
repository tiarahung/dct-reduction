# dct-reduction
A package for reducing DCT DeVeny images. Currently only supports images observed with 1.5" slit and the 300g/mm grating. Most scripts wrap around PyRAF/IRAF functions thus would only work in Python 2.

 
Tested with PyRAF 2.1.15.


## Before starting

Create an iraf environment with conda. Make sure you configure Conda to use the Astroconda Channel first (see [STscI documentation](https://astroconda.readthedocs.io/en/latest/installation.html#configure-conda-to-use-the-astroconda-channel)).

```
conda create -n iraf27 python=2.7 iraf-all pyraf-all stsci
```

Copy the cl files to the iraf directory
```
cp cl/DCTlines.dat /usr/local/miniconda2/envs/iraf27/iraf/noao/lib/linelists
```

```
cp cl/obsdb.dat /usr/local/miniconda2/envs/iraf27/iraf/noao/lib/obsdb.dat
```

## Quick start

**Important:** Make sure you have activated iraf27 environment
```
conda activate iraf27
```
- Clone this repository to your local directory. 
```
git clone https://github.com/tiarahung/dct-reduction.git
```
- Export path to **dct-reduction**
```
export dct_reduction = <path-to-the-directory-you-just-downloaded>
```

- Now switch to the raw frames (flat-field, science, arc, flux standard) directory

**Important:** Make sure to **remove** all the _irrelevant files_ (such as the focus loop products that will not be used for calibration) before calling any of the scripts.)

- The first step is to prepare all the files for reduction.  Type and run in a terminal
```
python $dct_reduction/pre_reduce.py
```
> This generates a CCD response image (flat-fielding), a combined arc lamp frame, and a text file containing a list of objects in this directory. 

- The second step is to make the flux calibration file.
```
python $dct_reduction/mkfluxcal.py -f 0063 0064
```
> In this example, your standard star files are 2019xxxx.**0063**.fits and  2019xxxx.**0064**.fits. You will be asked to extract a star of your choice. Do not change any parameters in line identification (for solving the wavelength) as the program will apply a final offset according to the sky lines. 

> Telluric features are removed in this step, generating files with the prefix 't'.

- The third step will take 2D science frames and output a 1D spectrum.
```
python $dct_reduction/extract_src.py -f 0066 0067 0068
```
> In this step, the file numbers should belong to **one single target**. The script extracts each frame individually and combine them in the end.

> The name of the final combined spectrum has the form _SCITARG_flux.fits_.
Since all the calibration files are produced in step 1 and 2. You only need to repeat step 3 for each science target. 
