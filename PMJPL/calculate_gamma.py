from typing import Union
import numpy as np

from daily_evapotranspiration_upscaling import lambda_Jkg_from_Ta_C

from rasters import Raster

SPECIFIC_HEAT_CAPACITY_AIR = 1013 # J kg-1 K-1, Monteith & Unsworth (2001)
MOL_WEIGHT_WET_DRY_RATIO_AIR = 0.622

def calculate_gamma(
        Ta_C: Union[Raster, np.ndarray],
        Ps_Pa: Union[Raster, np.ndarray],
        Cp_Jkg: Union[Raster, np.ndarray, float] = SPECIFIC_HEAT_CAPACITY_AIR,
        RMW: Union[Raster, np.ndarray, float] = MOL_WEIGHT_WET_DRY_RATIO_AIR) -> Union[Raster, np.ndarray]:
    """
    Calculate the psychrometric constant (gamma) for evapotranspiration modeling.
    
    The psychrometric constant is a fundamental parameter in atmospheric physics that
    quantifies the relationship between sensible and latent heat transfer in the atmosphere.
    It is essential for the Penman-Monteith equation and other evapotranspiration models,
    representing the ratio of specific heat of moist air to the latent heat of vaporization
    multiplied by the ratio of molecular weights of water vapor to dry air.
    
    Mathematical Formula:
    γ = (Cp × P) / (λ × ε)
    
    Where:
    - γ = psychrometric constant (Pa K⁻¹)
    - Cp = specific heat capacity of air at constant pressure (J kg⁻¹ K⁻¹)
    - P = atmospheric pressure (Pa)
    - λ = latent heat of vaporization of water (J kg⁻¹)
    - ε = ratio of molecular weight of water vapor to dry air (≈ 0.622)
    
    Physical Significance:
    The psychrometric constant is temperature and pressure dependent, making it crucial
    for accurate evapotranspiration calculations across diverse environmental conditions.
    It accounts for:
    - Temperature effects on latent heat of vaporization (Clausius-Clapeyron relation)
    - Elevation effects through atmospheric pressure variations
    - Energy partitioning between sensible and latent heat fluxes
    
    This implementation is part of the MOD16 evapotranspiration algorithm used by
    NASA's ECOSTRESS mission and is designed for processing high-resolution remote
    sensing imagery.
    
    Parameters
    ----------
    Ta_C : Union[Raster, np.ndarray]
        Air temperature in degrees Celsius. Used to calculate the temperature-dependent
        latent heat of vaporization through the Clausius-Clapeyron equation.
        
    Ps_Pa : Union[Raster, np.ndarray]
        Surface atmospheric pressure in Pascals. Accounts for elevation effects on
        evapotranspiration rates. Lower pressure at higher elevations reduces the
        psychrometric constant.
        
    Cp_Jkg : Union[Raster, np.ndarray, float], optional
        Specific heat capacity of air at constant pressure in J kg⁻¹ K⁻¹.
        Default: 1013 J kg⁻¹ K⁻¹ (Monteith & Unsworth, 2001).
        This represents the amount of energy required to raise the temperature
        of 1 kg of air by 1 K at constant pressure.
        
    RMW : Union[Raster, np.ndarray, float], optional
        Ratio of molecular weights of water vapor to dry air (dimensionless).
        Default: 0.622 (18.016 g/mol ÷ 28.97 g/mol).
        This constant accounts for the different molecular masses affecting
        vapor pressure relationships.
    
    Returns
    -------
    Union[Raster, np.ndarray]
        Psychrometric constant in Pa K⁻¹. Values typically range from 60-70 Pa K⁻¹
        at sea level and standard temperature, increasing with elevation and
        decreasing with temperature.
    
    Notes
    -----
    The psychrometric constant is used extensively in:
    - Penman-Monteith equation for reference evapotranspiration
    - Energy balance calculations for partitioning available energy
    - Vapor pressure deficit relationships for atmospheric moisture demand
    - Canopy conductance models for transpiration calculations
    
    The temperature dependency through λ(T) is critical because:
    - Higher temperatures decrease latent heat of vaporization
    - This affects evapotranspiration rates and energy partitioning
    - Accurate temperature relationships are essential for global applications
    
    References
    ----------
    .. [1] Monteith, J. L., & Unsworth, M. H. (2001). Principles of Environmental 
           Physics (3rd ed.). Academic Press.
    .. [2] Mu, Q., Zhao, M., & Running, S. W. (2011). Improvements to a MODIS 
           global terrestrial evapotranspiration algorithm. Remote Sensing of 
           Environment, 115(8), 1781-1800. doi:10.1016/j.rse.2011.02.019
    .. [3] Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). Crop 
           evapotranspiration - Guidelines for computing crop water requirements. 
           FAO Irrigation and drainage paper 56.
    .. [4] Penman, H. L. (1948). Natural evaporation from open water, bare soil 
           and grass. Proceedings of the Royal Society of London, 193(1032), 120-145.
    
    Examples
    --------
    >>> import numpy as np
    >>> from rasters import Raster
    >>> 
    >>> # Calculate gamma for standard conditions
    >>> Ta_C = np.array([20.0, 25.0, 30.0])  # Air temperature in Celsius
    >>> Ps_Pa = np.array([101325, 101325, 101325])  # Sea level pressure
    >>> gamma = calculate_gamma(Ta_C, Ps_Pa)
    >>> print(f"Psychrometric constant: {gamma} Pa K⁻¹")
    >>> 
    >>> # For high elevation (lower pressure)
    >>> Ps_Pa_high = np.array([85000, 85000, 85000])  # ~1500m elevation
    >>> gamma_high = calculate_gamma(Ta_C, Ps_Pa_high)
    >>> print(f"High elevation gamma: {gamma_high} Pa K⁻¹")
    
    See Also
    --------
    lambda_Jkg_from_Ta_C : Calculate latent heat of vaporization from temperature
    delta_Pa_from_Ta_C : Calculate slope of saturation vapor pressure curve
    """
    # calculate latent heat of vaporization (J kg-1)
    lambda_Jkg = lambda_Jkg_from_Ta_C(Ta_C)
    gamma =  (Cp_Jkg * Ps_Pa) / (lambda_Jkg * RMW)
    
    return gamma