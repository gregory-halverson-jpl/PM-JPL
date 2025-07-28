from typing import Union
import rasters as rt
from rasters import Raster
import numpy as np

# NDVI value for full vegetation (typical for dense green canopy)
NDVIv = 0.52  # ± 0.03

# NDVI value for bare soil (typical for non-vegetated surfaces)
NDVIs = 0.04  # ± 0.03

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
    FVC = rt.clip((NDVI - NDVIs) / (NDVIv - NDVIs), 0.0, 1.0)
    return FVC
