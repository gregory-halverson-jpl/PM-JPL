from typing import Union
import numpy as np
import rasters as rt
from rasters import Raster

KPAR = 0.5
MIN_FIPAR = 0.0
MAX_FIPAR = 1.0
MIN_LAI = 0.0
MAX_LAI = 10.0

def carlson_fractional_vegetation_cover(NDVI: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Converts Normalized Difference Vegetation Index (NDVI) to Fractional Vegetation Cover (FVC) using a linear scaling method.

    Explanation:
        This function estimates the fraction of ground covered by vegetation (FVC) from NDVI values. It linearly scales NDVI between two reference values:
        - NDVIv: NDVI of fully vegetated surface (here, 0.52 ± 0.03)
        - NDVIs: NDVI of bare soil (here, 0.04 ± 0.03)
        The formula is:
            FVC = clip((NDVI - NDVIs) / (NDVIv - NDVIs), 0.0, 1.0)
        Values below NDVIs are set to 0 (bare soil), above NDVIv to 1 (full vegetation), and in between are linearly scaled.

    Constants:
        NDVIv (float): NDVI value for full vegetation (0.52 ± 0.03). See Carlson & Ripley (1997).
        NDVIs (float): NDVI value for bare soil (0.04 ± 0.03). See Carlson & Ripley (1997).

    Citation:
        Carlson, T.N., & Ripley, D.A. (1997). On the relation between NDVI, fractional vegetation cover, and leaf area index. Remote Sensing of Environment, 62(3), 241-252. https://doi.org/10.1016/S0034-4257(97)00104-1

    Parameters:
        NDVI (Union[Raster, np.ndarray]): Input NDVI data.

    Returns:
        Union[Raster, np.ndarray]: Converted FVC data.
    """
    NDVIv = 0.52  # +- 0.03
    NDVIs = 0.04  # +- 0.03
    FVC = rt.clip((NDVI - NDVIs) / (NDVIv - NDVIs), 0.0, 1.0)

    return FVC

def carlson_leaf_area_index(
        NDVI: Union[Raster, np.ndarray],
        min_fIPAR: float = MIN_FIPAR,
        max_fIPAR: float = MAX_FIPAR,
        min_LAI: float = MIN_LAI,
        max_LAI: float = MAX_LAI) -> Union[Raster, np.ndarray]:
    """
    Converts Normalized Difference Vegetation Index (NDVI) to Leaf Area Index (LAI) using a two-step process:

    Explanation:
        1. Estimate fIPAR (fraction of absorbed photosynthetically active radiation) from NDVI:
           fIPAR = clip(NDVI - 0.05, min_fIPAR, max_fIPAR)
           This linear relationship is commonly used in remote sensing to relate NDVI to canopy light absorption.
        2. Calculate LAI using the Beer-Lambert law:
           LAI = -ln(1 - fIPAR) / KPAR
           The Beer-Lambert law describes how light is attenuated through a medium (here, a plant canopy). KPAR is the extinction coefficient for PAR (typically 0.5).
        3. Results are clipped to the specified min/max LAI range.

    Constants:
        KPAR (float): Extinction coefficient for PAR (default 0.5). See Goudriaan (1977).
        MIN_FIPAR, MAX_FIPAR (float): Minimum and maximum fIPAR values (default 0.0, 1.0).
        MIN_LAI, MAX_LAI (float): Minimum and maximum LAI values (default 0.0, 10.0).

    Citations:
        - Carlson, T.N., & Ripley, D.A. (1997). On the relation between NDVI, fractional vegetation cover, and leaf area index. Remote Sensing of Environment, 62(3), 241-252. https://doi.org/10.1016/S0034-4257(97)00104-1
        - Monsi, M., & Saeki, T. (1953). Über den Lichtfaktor in den Pflanzengesellschaften und seine Bedeutung für die Stoffproduktion. Japanese Journal of Botany, 14, 22-52.
        - Goudriaan, J. (1977). Crop Micrometeorology: A Simulation Study.

    Parameters:
        NDVI (Union[Raster, np.ndarray]): Input NDVI data.
        min_fIPAR (float): Minimum fIPAR value (default 0.0).
        max_fIPAR (float): Maximum fIPAR value (default 1.0).
        min_LAI (float): Minimum LAI value (default 0.0).
        max_LAI (float): Maximum LAI value (default 10.0).

    Returns:
        Union[Raster, np.ndarray]: Converted LAI data.
    """
    # Step 1: Estimate fIPAR from NDVI, using a linear relationship and clip to valid range
    fIPAR = rt.clip(NDVI - 0.05, min_fIPAR, max_fIPAR)  # NDVI offset by 0.05, clipped to [min_fIPAR, max_fIPAR]
    # Step 2: Set fIPAR=0 to NaN (no absorption, no vegetation)
    fIPAR = np.where(fIPAR == 0, np.nan, fIPAR)         # Avoid log(0) in next step
    # Step 3: Calculate LAI using Beer-Lambert law, then clip to valid LAI range
    LAI = rt.clip(-np.log(1 - fIPAR) * (1 / KPAR), min_LAI, max_LAI)  # Beer-Lambert law for canopy

    return LAI
