import numpy as np
import argparse
import matplotlib.pyplot as plt

from astroplan.plots import plot_finder_image
from astroplan import FixedTarget

from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.coordinates import Angle

"""
	Create Finding Charts for observation purposes from a file containing the 
	target list in the first column, and optionally the RA and DEC in columns 2 and 3 

    Parameters
    ----------
	file:	Either path to the file where the list of targets is or a target ID 
			that can be resolved by Simbad.
	
    OPTIONAL parameters
    --------------------
    --COORD:	By default it uses the target name to look for the target in Simbad
    			If --COORD is provided, then it will use the coordinates in 
    			Columns 2 and 3
    --fov		Field of view to plot in the Finding Chart [arcmin]. Default = 7 
    
    Returns
    -------
	Plots in jpeg 
	
"""

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="File name containing the target list")
    parser.add_argument('--fov', type=float, default=7, help='Field of view in arcmin')
    parser.add_argument("-C", "--COORD", help="From coordinates", action="store_true")
    args = parser.parse_args()
    return args

def sexa2deg(x):
    """Transform equatorial coordinates from sexagesimal strings to degrees.

    Parameters
    ----------
    x : string array
        Either a single pair of coordinate strings in a 1D array like ``[dec,
        ra]``, or a 2D array of multiple (dec,ra) coordinate strings, ordered
        like ``[[dec1,ra1], [dec2,ra2], ...]``. In each coordinate pair, the
        declination string should be written like degrees:minutes:seconds, and
        the right-ascension string should be written like
        hours:minutes:seconds.

    Returns
    -------
    out : array of numbers
        The array of ra,dec coordinates in degrees, returned in an
        array of the same dimensions as the input array.

    """
    x = np.asarray(x)
    ndim = x.ndim
    x = np.atleast_2d(x)

    result = []
    for i in range(np.shape(x)[0]):
        ra = hms2deg(x[i][0])
        dec = dms2deg(x[i][1])
        result.append(np.array([ra, dec]))
    return np.array(result) if ndim > 1 else result[0]

def hms2deg(x):
    """Transform *hours:minutes:seconds* strings to degrees.

    Parameters
    ----------
    x : str
        The input angle, written in the form, hours:minutes:seconds

    Returns
    -------
    out : float
        The angle as a number of degrees.

    """
    ac = Angle(x, unit='hour')
    deg = float(ac.to_string(unit='degree', decimal=True))
    return deg

def dms2deg(x):
    """Transform *degrees:arcminutes:arcseconds* strings to degrees.

    Parameters
    ----------
    x : str
        The input angle written in the form, degrees:arcminutes:arcseconds

    Returns
    -------
    out : float
        The input angle as a number of degrees.

    """
    ac = Angle(x, unit='degree')
    deg = float(ac.to_string(unit='degree', decimal=True))
    return deg


if "__main__":

	args = cli()
	fov = args.fov

	try:
		targets = np.genfromtxt(args.file,dtype=None)
	except:
		targets = np.atleast_2d(np.array([args.file, "0:0:0", "0:0:0"]))

	for t in targets:
		objname = t[0].upper()
		
		# From coordinates
		if args.COORD:
			ra,dec = t[1], t[2]
			try:
				radeg 	= ra.astype('float')
				decdeg 	= dec.astype('float')
			except:
				radeg,decdeg = sexa2deg([ra,dec])
			mycoord = SkyCoord(ra=radeg*u.deg,dec=decdeg*u.deg,frame='fk5')
			object = FixedTarget(coord=mycoord, name=t[0].upper())

		# From object name
		else:
			object = FixedTarget.from_name(objname)
		ax, hdu = plot_finder_image(object,reticle=True,fov_radius=fov*u.arcmin)
		plt.savefig(objname+'.jpg')
		plt.close()
