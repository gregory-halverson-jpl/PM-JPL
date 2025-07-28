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

def LAI_from_NDVI(
        NDVI: Union[Raster, np.ndarray],
        min_fIPAR: float = MIN_FIPAR,
        max_fIPAR: float = MAX_FIPAR,
        min_LAI: float = MIN_LAI,
        max_LAI: float = MAX_LAI) -> Union[Raster, np.ndarray]:
    """
    Convert Normalized Difference Vegetation Index (NDVI) to Leaf Area Index (LAI).

    Parameters:
        NDVI (Union[Raster, np.ndarray]): Input NDVI data.

    Returns:
        Union[Raster, np.ndarray]: Converted LAI data.
    """
    fIPAR = rt.clip(NDVI - 0.05, min_fIPAR, max_fIPAR)
    fIPAR = np.where(fIPAR == 0, np.nan, fIPAR)
    LAI = rt.clip(-np.log(1 - fIPAR) * (1 / KPAR), min_LAI, max_LAI)

    return LAI
