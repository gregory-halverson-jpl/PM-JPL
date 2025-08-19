from typing import Union
from os.path import join, abspath, dirname
import numpy as np
import pandas as pd

from rasters import Raster, RasterGeometry, SpatialGeometry

from MCD12C1_2019_v006 import load_MCD12C1_IGBP

from .constants import *

LUT = pd.read_csv(join(abspath(dirname(__file__)), 'mod16.csv'))

def PMJPL_parameter_from_IGBP(
        variable: str, 
        IGBP: Union[Raster, np.ndarray] = None, 
        geometry: SpatialGeometry = None, 
        resampling=IGBP_PARAMETER_RESAMPLING) -> Union[Raster, np.ndarray]:
    """
    Translates the IGBP (International Geosphere-Biosphere Programme) values to the corresponding values in the Look-Up Table (LUT) for a given variable.

    Parameters:
        variable (str): The variable for which the translation is performed.
            gl_sh (m s-1 LAI-1) Leaf conductance to sensible heat per unit LAI
            gl_e_wv (m s-1 LAI-1) Leaf conductance to evaporated water per unit LAI
            rbl_min (s m-1) Minimum atmospheric boundary layer resistance
            rbl_max (s m-1) Maximum atmospheric boundary layer resistance
            cl (m s-1) Mean potential stomatal conductance per unit leaf area
            tmin_open (deg C) Temperature at which stomata are completely open, i.e., there is no effect of temperature on transpiration
            tmin_close (deg C) Temperature at which stomata are almost completely closed due to (minimum) temperature stress
            vpd_close (Pa) The VPD at which stomata are almost completely closed due to water stress
            vpd_open (Pa) The VPD at which stomata are completely open, i.e., there is no effect of water stress on transpiration
        IGBP (Union[np.ndarray, Raster]): The IGBP values to be translated.

    Returns:
        Union[np.ndarray, Raster]: The translated values.
    """
    if geometry is None and isinstance(IGBP, Raster):
        geometry = IGBP.geometry

    if isinstance(geometry, RasterGeometry):
        IGBP_geometry = geometry.UTM(500)
    else:
        IGBP_geometry = geometry

    if IGBP is None:
        IGBP = load_MCD12C1_IGBP(geometry=IGBP_geometry)

    result = np.float32(np.array(LUT[variable])[np.array(IGBP).astype(int)])

    if isinstance(IGBP, Raster) or isinstance(geometry, RasterGeometry):
        result = Raster(result, geometry=IGBP_geometry)
        result = result.to_geometry(geometry, resampling=resampling)
    
    return result
