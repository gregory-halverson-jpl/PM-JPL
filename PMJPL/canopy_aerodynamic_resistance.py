from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

def calculate_canopy_aerodynamic_resistance(
    VPD_Pa: Union[Raster, np.ndarray],
    VPD_open_Pa: Union[Raster, np.ndarray],
    VPD_close_Pa: Union[Raster, np.ndarray],
    RBL_max: Union[Raster, np.ndarray],
    RBL_min: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate total canopy aerodynamic resistance based on vapor pressure deficit.
    
    This function computes the total aerodynamic resistance to the canopy as a 
    function of vapor pressure deficit (VPD) and biome-specific boundary layer resistance 
    parameters. The resistance varies between minimum and maximum values based on stomatal 
    response to atmospheric moisture demand, implementing a key component of the MOD16 
    evapotranspiration algorithm.
    
    **CRITICAL**: All VPD-related parameters must be in Pascals (Pa) to ensure correct 
    operation with MOD16 lookup table values. Using different pressure units will cause 
    incorrect stomatal response calculations.
    
    The aerodynamic resistance represents the resistance to water vapor and heat transfer 
    from the canopy to the atmosphere through the boundary layer. This parameter is crucial 
    for accurately modeling transpiration rates and energy partitioning in vegetation.
    
    Physical Mechanism:
    - At low VPD (high atmospheric humidity): Stomata remain open, resistance is maximum
    - At high VPD (low atmospheric humidity): Stomata close to conserve water, resistance is minimum
    - Between thresholds: Linear interpolation models gradual stomatal response
    
    Mathematical Implementation:
    - VPD_Pa ≤ VPD_open_Pa: resistance = RBL_max (stomata fully open)
    - VPD_Pa ≥ VPD_close_Pa: resistance = RBL_min (stomata mostly closed)
    - VPD_open_Pa < VPD_Pa < VPD_close_Pa: resistance = RBL_min + (RBL_max - RBL_min) × (VPD_close_Pa - VPD_Pa) / (VPD_close_Pa - VPD_open_Pa)
    
    This formulation captures the physiological response of plants to atmospheric dryness,
    where stomata progressively close as VPD increases to prevent excessive water loss,
    thereby increasing the resistance to water vapor transfer.
    
    Parameters
    ----------
    VPD_Pa : Union[Raster, np.ndarray]
        Vapor pressure deficit in Pascals (Pa). **UNITS ARE CRITICAL** - must be in 
        Pascals to match MOD16 lookup table thresholds. Represents the difference 
        between saturated and actual vapor pressure, indicating atmospheric moisture 
        demand. Higher VPD values indicate drier atmospheric conditions that stress 
        vegetation. Typical range: 100-5000 Pa.
        
        **Warning**: Using different units (e.g., kPa, hPa, or mb) will cause 
        incorrect results since direct numerical comparisons are made against 
        biome-specific thresholds defined in Pascals.
        
    VPD_open_Pa : Union[Raster, np.ndarray]
        VPD threshold in Pascals (Pa) below which stomata are completely open and 
        there is no water stress effect on transpiration. Biome-specific parameter 
        from MOD16 lookup table. Typical values: 650-1000 Pa.
        **Must be in same units as VPD_Pa parameter.**
        
    VPD_close_Pa : Union[Raster, np.ndarray] 
        VPD threshold in Pascals (Pa) above which stomata are almost completely 
        closed due to water stress. Biome-specific parameter from MOD16 lookup table.
        Typical values: 2900-4500 Pa.
        **Must be in same units as VPD_Pa parameter.**
        
    RBL_max : Union[Raster, np.ndarray]
        Maximum atmospheric boundary layer resistance in s m⁻¹. Applied when VPD is
        low (favorable conditions) and stomata are fully open. Biome-specific parameter
        representing maximum resistance to vapor transfer. Typical values: 45-100 s m⁻¹.
        
    RBL_min : Union[Raster, np.ndarray]
        Minimum atmospheric boundary layer resistance in s m⁻¹. Applied when VPD is
        high (water stress conditions) and stomata are mostly closed. Biome-specific
        parameter representing minimum resistance to vapor transfer. 
        Typical values: 20-70 s m⁻¹.
    
    Returns
    -------
    Union[Raster, np.ndarray]
        Total canopy aerodynamic resistance in s m⁻¹. Higher values indicate
        greater resistance to water vapor and heat transfer from canopy to atmosphere.
        Values range between RBL_min and RBL_max depending on VPD conditions.
    
    Notes
    -----
    The function implements a three-piece piecewise linear function that models the
    physiological response of vegetation to atmospheric water demand:
    
    1. **Low VPD regime** (VPD_Pa ≤ VPD_open_Pa): Optimal conditions where stomata remain
       fully open and resistance is at maximum, allowing efficient photosynthesis
       with minimal water stress.
       
    2. **High VPD regime** (VPD_Pa ≥ VPD_close_Pa): Severe water stress conditions where
       stomata close to conserve water, reducing resistance to minimum values and
       limiting transpiration.
       
    3. **Intermediate VPD regime** (VPD_open_Pa < VPD_Pa < VPD_close_Pa): Transitional zone
       where stomata gradually close as atmospheric demand increases, following a
       linear relationship between the threshold values.
    
    This formulation is essential for:
    - Accurate transpiration modeling under varying atmospheric conditions
    - Energy balance calculations in land surface models
    - Water stress assessment in vegetation monitoring
    - Climate impact studies on ecosystem water use
    
    The biome-specific parameters (VPD_open_Pa, VPD_close_Pa, RBL_min, RBL_max) are derived
    from the MOD16 lookup table based on IGBP land cover classifications, allowing
    the model to account for different vegetation types' physiological responses.
    
    References
    ----------
    .. [1] Mu, Q., Zhao, M., & Running, S. W. (2011). Improvements to a MODIS 
           global terrestrial evapotranspiration algorithm. Remote Sensing of 
           Environment, 115(8), 1781-1800. doi:10.1016/j.rse.2011.02.019
    .. [2] Mu, Q., Heinsch, F. A., Zhao, M., & Running, S. W. (2007). Development 
           of a global evapotranspiration algorithm based on MODIS and global 
           meteorology data. Remote Sensing of Environment, 111(4), 519-536.
    .. [3] Monteith, J. L. (1995). A reinterpretation of stomatal responses to 
           humidity. Plant, Cell & Environment, 18(4), 357-364.
    .. [4] Ball, J. T., Woodrow, I. E., & Berry, J. A. (1987). A model predicting 
           stomatal conductance and its contribution to the control of photosynthesis 
           under different environmental conditions. Progress in Photosynthesis 
           Research, 4, 221-224.
    
    Examples
    --------
    >>> import numpy as np
    >>> from rasters import Raster
    >>> 
    >>> # Example for grassland (IGBP class 10)
    >>> VPD_Pa = np.array([500, 1500, 3000, 5000])  # Pa
    >>> VPD_open_Pa = np.array([650, 650, 650, 650])  # Pa (grassland threshold)
    >>> VPD_close_Pa = np.array([4200, 4200, 4200, 4200])  # Pa (grassland threshold)
    >>> RBL_max = np.array([50, 50, 50, 50])  # s/m (grassland maximum)
    >>> RBL_min = np.array([20, 20, 20, 20])  # s/m (grassland minimum)
    >>> 
    >>> rtotc = calculate_canopy_aerodynamic_resistance(VPD_Pa, VPD_open_Pa, VPD_close_Pa, RBL_max, RBL_min)
    >>> print(f"Aerodynamic resistance: {rtotc} s/m")
    >>> # Expected: [50, ~36, ~22, 20] - decreasing resistance with increasing VPD
    >>> 
    >>> # Demonstrate VPD stress response
    >>> VPD_stress = np.linspace(0, 5000, 100)  # Full VPD range
    >>> rtotc_response = calculate_canopy_aerodynamic_resistance(VPD_stress, 650, 4200, 50, 20)
    >>> # Shows smooth transition from 50 to 20 s/m as VPD increases
    
    See Also
    --------
    MOD16_parameter_from_IGBP : Retrieve biome-specific parameters from lookup table
    calculate_rcorr : Calculate resistance correction factor
    calculate_VPD_factor : Calculate VPD-based stress factor
    """
    rtotc = rt.where(VPD_Pa <= VPD_open_Pa, RBL_max, np.nan)
    rtotc = rt.where(VPD_Pa >= VPD_close_Pa, RBL_min, rtotc)

    rtotc = rt.where(
        np.logical_and(VPD_open_Pa < VPD_Pa, VPD_Pa < VPD_close_Pa),
        RBL_min + (RBL_max - RBL_min) * (VPD_close_Pa - VPD_Pa) / (VPD_close_Pa - VPD_open_Pa),
        rtotc
    )

    return rtotc