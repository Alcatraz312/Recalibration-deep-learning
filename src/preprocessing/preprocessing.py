import numpy as np
import pandas as pd

from scipy.interpolate import CubicSpline
from scipy.ndimage import gaussian_filter1d

from astropy.io import fits

import matplotlib.pyplot as plt

def preprocess(star_path):
    with fits.open(star_path) as star_data:
        hdr = star_data[0].header
        flux = star_data[0].data

        n_wave_points = len(flux)

        crval = hdr["CRVAL1"]
        cdelt = hdr["CDELT1"]

        wavelength = crval + cdelt * np.arange(n_wave_points)

        # degrading the FWHM resolution of CFLIB 

        cflib_res_fwhm = 0.88                   # intrinsic resolution of the CFLIB library (FWHM)
        cflib_int_res_fwhm = 2.56               # resolution of the interpolated CFLIB flux (FWHM) based on MILES

        def var(res_fwhm):          # relation between variance and FWHM
            return res_fwhm/(2*np.log(2))
    
        cflib_conv_res_fwhm = ((cflib_int_res_fwhm)**2 - (cflib_res_fwhm)**2) ** 1/2            # resolution FWHM of the gaussian Kernel

        var_conv_res_fwhm = var(cflib_conv_res_fwhm)                # variance of the the FWHM of the gaussian kernel 

        var_pixel = var_conv_res_fwhm/cdelt                     # variance per pixel 

        filtered_flux = gaussian_filter1d(flux, sigma = var_pixel)          # Convolution with the gaussian Kernel to degrade the resolution

        # Resampling the data using cubic spline interpolation

        cs = CubicSpline(wavelength, filtered_flux)          # defining the cs object

        new_wavelength = np.arange(3465,9469, 0.9)      # defining a new wavelength grid
    
        filtered_flux_resampled = cs(new_wavelength)         # applying cubic spline interpolation on the new wavelenth to get the new resampled flux

        # Normalizing the flux at wavelenth value of approx 5550 A

        index = 0

        for i in range(len(new_wavelength)):
            if new_wavelength[i] == 5550.30000000021:
                index = i

        normalized_flux = filtered_flux_resampled/filtered_flux_resampled[index]              # normalizing the flux axis at approx 5550 A value of wavelength

        # Changing the coverage of the new wavelength grid

        mask = (new_wavelength >= 3536.0) & (new_wavelength <= 7410.600000000399)
        final_wavelength = new_wavelength[mask]         # new wavelength grid with step value of 0.9

        final_flux = normalized_flux[mask]

        return final_wavelength, final_flux
    
# wavelength, flux = preprocess("./FITS_data/5750.fits")

# plt.plot(wavelength, flux)

# plt.show()
    

    

