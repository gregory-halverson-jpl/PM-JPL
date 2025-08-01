from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

def calculate_correctance_factor(
        Ps_Pa: Union[Raster, np.ndarray], 
        Ta_K: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate the correction factor (rcorr) for stomatal and cuticular conductances
    based on surface atmospheric pressure and air temperature.

    This factor adjusts leaf conductance values from standard reference conditions
    (sea level pressure, 20°C) to actual environmental conditions, accounting for
    the effects of pressure and temperature on the diffusivity of water vapor in air.

    Physical Basis
    -------------
    - Lower atmospheric pressure (e.g., high elevation) increases the diffusivity of gases, so conductance must be scaled up.
    - Higher temperature increases molecular motion and the rate of diffusion, also requiring scaling.
    - The correction factor ensures that modeled or measured conductances are physically consistent across different elevations and climates.

    Mathematical Structure
    ---------------------
    The formula is:
        rcorr = 1 / ((101300 / Ps_Pa) * (Ta_K / 293.15) ** 1.75)
    Where:
        Ps_Pa : surface atmospheric pressure in Pascals
        Ta_K  : near-surface air temperature in Kelvin
        101300: reference pressure (Pa, sea level)
        293.15: reference temperature (K, 20°C)
        1.75  : exponent for temperature dependence of water vapor diffusivity in air

    Parameters
    ----------
    Ps_Pa : Union[Raster, np.ndarray]
        Surface atmospheric pressure in Pascals (Pa).
    Ta_K : Union[Raster, np.ndarray]
        Near-surface air temperature in Kelvin (K).

    Returns
    -------
    Union[Raster, np.ndarray]
        Correction factor (rcorr), dimensionless. Used to scale stomatal and cuticular conductances to local conditions.

    Notes
    -----
    - Used in MOD16 and similar evapotranspiration models to adjust leaf conductance parameters for local meteorological conditions.
    - Ensures physical consistency in remote sensing and land surface models across different elevations and climates.
    - Based on the physical principles of gas diffusion (Fick's law) and empirical temperature/pressure dependence of water vapor diffusivity.

    References
    ----------
    Monteith, J. L., & Unsworth, M. H. (2001). Principles of Environmental Physics (3rd ed.). Academic Press.
    Mu, Q., Zhao, M., & Running, S. W. (2011). Improvements to a MODIS global terrestrial evapotranspiration algorithm. Remote Sensing of Environment, 115(8), 1781-1800.
    Jones, H. G. (2013). Plants and Microclimate: A Quantitative Approach to Environmental Plant Physiology (3rd ed.). Cambridge University Press.
    Farquhar, G. D., & Sharkey, T. D. (1982). Stomatal conductance and photosynthesis. Annual Review of Plant Physiology, 33(1), 317-345.

    Example
    -------
        >>> Ps_Pa = 90000.0  # Pa (high elevation)
        >>> Ta_K = 303.15    # K (30°C)
        >>> rcorr = calculate_correctance_factor(Ps_Pa, Ta_K)
        >>> print(rcorr)
    """
    return 1.0 / ((101300.0 / Ps_Pa) * (Ta_K / 293.15) ** 1.75)
