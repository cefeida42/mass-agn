import numpy as np

def MJD_convert(mjd, time='days'):
    "Convert Modified Julian Date to days or hours, starting from the first data point in the given array"
    if time=='days':
        return mjd - mjd.min() # Converting MJD to days
    elif time=='hours':
        return (mjd - mjd.min())*24
    else:
        print("Error: Keyword argument 'time' is not valid, choose --> {'days', 'hours'})")
            
def mag_to_flux(mag, filt, phot_sys='SDSS'):

    if filt=='u':
        return 10**((24.63 - mag)/2.5)
    elif filt =='g':
        return 10**((25.11 - mag)/2.5)
    elif filt == 'r':
        return 10**((24.80 - mag)/2.5)
    elif filt == 'i':
        return 10**((24.36 - mag)/2.5)
    elif filt == 'z':
        return 10**((22.83 - mag)/2.5)
    
def flux_to_mag(flux, filt, phot_sys='SDSS'):
    if filt == 'u':
        return 24.63 - 2.5*np.log10(flux)
    elif filt =='g':
        return 25.11 - 2.5*np.log10(flux)
    elif filt == 'r':
        return 24.80 - 2.5*np.log10(flux)
    elif filt == 'i':
        return 24.36 - 2.5*np.log10(flux)
    elif filt == 'z':
        return 22.83 - 2.5*np.log10(flux)
    
def lc_prep(t, intensity, filt, mag_flux=True, flux_mag=False, mjd_convert=True, time='days',  norm=False, phot_sys='SDSS'):
    if mag_flux == True:
        intensity = mag_to_flux(intensity, filt, phot_sys=phot_sys)
    if flux_mag == True:
        intensity = flux_to_mag(intensity, filt, phot_sys=phot_sys)
    if mjd_convert == True:
        t = MJD_convert(t, time=time)
    if norm == True:
        intensity == (intensity - intensity.min())/(intensity.max() - intensity.min())
    return t, intensity
    

def lc_proc(lcs, filters, time='hours'):
    """
    Process a list of light curves from Edri et al. (2012). Each light curve 
    is stored as a pandas dataframe.
    
    Parameters:
    -----------
    lcs: list (elements assumed to be pd.DataFrame objects)
        A list of light curves. Each light curve is a pd.DataFrame with columns:
        MJD, mag, mag_err
    filters: str
        Corresponding filter names for light curves (possible vals: 'r', 'g', 'i')
    time: str
        Time unit to convert into. Default is 'hours'.
        
    Returns:
    --------
    lcs: list
        A list of input light curves with added columns: time_hours, flux, 
        flux_err, norm_flux, norm_flux_err

    """
    # We will do conversions for all filters
    for lc, filt in zip(lcs, filters):
        t, intensity = lc_prep(lc['MJD'], lc['mag'],
                           filt=filt,
                           mag_flux=True, 
                           mjd_convert=True, 
                           time=time)
    
        # Add new columns to dataframes:
        lc['time_{}'.format(time)] = t
        lc['flux'] = intensity

        # Calculate flux error using formula obtained by error propagation (mag. err. = flux_err/flux)
        lc['flux_err'] = lc['flux'] * np.abs(lc['mag_err'])

        # Add normalized flux and its error
        lc['norm_flux'] = (lc['flux'] - lc['flux'].min())/(lc['flux'].max() - lc['flux'].min())
        lc['norm_flux_err'] = (1/(lc['flux'].max()-lc['flux'].min()))*lc['flux_err']
    
    return lcs
