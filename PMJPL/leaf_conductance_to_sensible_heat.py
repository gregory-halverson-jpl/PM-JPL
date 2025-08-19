"""
leaf_conductance_to_sensible_heat.py

Provides a function to query leaf conductance to sensible heat (gl_sh) for a given biome and geometry, as used in the MOD16 evapotranspiration model.

Scientific Explanation:
----------------------
Leaf conductance to sensible heat (gl_sh) is a critical parameter in land surface models of evapotranspiration, representing the ability of leaves to transfer heat to the surrounding air via molecular diffusion and turbulent exchange. Sensible heat flux from leaves is governed by both stomatal and boundary layer conductances, which are influenced by leaf morphology, canopy structure, and environmental conditions (Monteith & Unsworth, 2013).

In the MOD16 algorithm (Mu et al., 2011), biome-specific values for gl_sh are derived from empirical studies and land cover classifications (IGBP), allowing for spatially explicit modeling of energy partitioning between latent and sensible heat. Accurate estimation of gl_sh is essential for modeling canopy energy balance, as it affects the calculation of wet canopy resistance and ultimately the partitioning of available energy into evapotranspiration components (Running et al., 1999; Mu et al., 2011).

References:
-----------
- Monteith, J.L., & Unsworth, M.H. (2013). Principles of Environmental Physics (4th Edition). Academic Press.
- Mu, Q., Zhao, M., & Running, S.W. (2011). Improvements to a MODIS global terrestrial evapotranspiration algorithm. Remote Sensing of Environment, 115(8), 1781-1800. https://doi.org/10.1016/j.rse.2011.02.019
- Running, S.W., Thornton, P.E., Nemani, R., & Glassy, J.M. (1999). Global terrestrial gross and net primary productivity from the Earth Observing System. In: Methods in Ecosystem Science (pp. 44-57). Springer.
"""
from .PMJPL_parameter_from_IGBP import PMJPL_parameter_from_IGBP

from typing import Optional, Union
import numpy as np
from rasters import Raster, RasterGeometry, VectorGeometry

from .constants import *

def leaf_conductance_to_sensible_heat(
    IGBP: Optional[Union[Raster, np.ndarray]] = None,
    geometry: Optional[Union[RasterGeometry, VectorGeometry]] = None,
    resampling: str = IGBP_PARAMETER_RESAMPLING
) -> Optional[Union[Raster, np.ndarray]]:
    """
    Query leaf conductance to sensible heat (gl_sh) for a given biome and geometry.

    Leaf conductance to sensible heat (gl_sh) is a biome-specific parameter representing the rate at which leaves transfer sensible heat to the atmosphere. It is essential for modeling canopy energy balance and evapotranspiration in land surface models such as MOD16 (Mu et al., 2011).

    Parameters
    ----------
    IGBP : Raster or np.ndarray
        International Geosphere-Biosphere Programme (IGBP) land cover classification.
    geometry : RasterGeometry or VectorGeometry
        Spatial geometry for the query.

    Returns
    -------
    gl_sh : Raster or np.ndarray
        Leaf conductance to sensible heat (seconds per meter).

    References
    ----------
    - Monteith, J.L., & Unsworth, M.H. (2013). Principles of Environmental Physics (4th Edition). Academic Press.
    - Mu, Q., Zhao, M., & Running, S.W. (2011). Improvements to a MODIS global terrestrial evapotranspiration algorithm. Remote Sensing of Environment, 115(8), 1781-1800.
    - Running, S.W., Thornton, P.E., Nemani, R., & Glassy, J.M. (1999). Global terrestrial gross and net primary productivity from the Earth Observing System. In: Methods in Ecosystem Science (pp. 44-57). Springer.
    """
    return PMJPL_parameter_from_IGBP(
        variable="gl_sh",
        IGBP=IGBP,
        geometry=geometry
    )
