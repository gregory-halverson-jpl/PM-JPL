import numpy as np
from typing import Union
from .constants import MAX_RESISTANCE
import rasters as rt
from rasters import Raster

def calculate_canopy_conductance(
    LAI: Union[Raster, np.ndarray],
    fwet: Union[Raster, np.ndarray],
    gl_sh: Union[Raster, np.ndarray],
    gs1: Union[Raster, np.ndarray],
    Gcu: Union[Raster, np.ndarray]) -> Union[Raster, np.ndarray]:
    """
    Calculate canopy conductance (Cc) to transpired water vapor per unit leaf area index (LAI).

    Canopy conductance (Cc) quantifies the ease with which water vapor moves from the leaf interior,
    through stomata and cuticle, across the leaf boundary layer, and into the atmosphere. It is a key
    control on plant transpiration and ecosystem water fluxes, and is the inverse of surface resistance (rs)
    in the Penman-Monteith equation for evapotranspiration.

    Physical Basis:
    - Stomatal conductance (gs1): Rate of water vapor exit through stomata, regulated by plant physiology and environment.
    - Cuticular conductance (Gcu): Water vapor loss through the leaf cuticle, important when stomata are closed.
    - Leaf boundary layer conductance (gl_sh): Transfer of water vapor across the thin layer of still air adjacent to the leaf surface.
    - LAI (Leaf Area Index): Total leaf area per unit ground area, scaling conductance to the canopy level.
    - fwet (relative surface wetness): Fraction of leaf surface that is wet, reducing transpiration when wet.

    Mathematical Structure:
    Stomatal and cuticular conductances act in parallel, and their sum is in series with the leaf boundary layer conductance:
        Cc = gl_sh * (gs1 + Gcu) / (gs1 + gl_sh + Gcu) * LAI * (1.0 - fwet)
    - The parallel sum: (gs1 + Gcu)
    - The series combination: gl_sh * (gs1 + Gcu) / (gs1 + gl_sh + Gcu)
    - Scaled by LAI and reduced by the fraction of wet surface (1 - fwet)
    - If LAI or (1 - fwet) is zero, conductance is set to zero (no transpiration)
    - The result is clipped to a minimum value (1/MAX_RESISTANCE) to avoid extreme/unphysical values

    Parameters:
    LAI : Union[Raster, np.ndarray]
        Leaf area index (dimensionless). Total leaf area per unit ground area.
    fwet : Union[Raster, np.ndarray]
        Relative surface wetness (dimensionless, 0-1). Fraction of leaf surface that is wet.
    gl_sh : Union[Raster, np.ndarray]
        Leaf boundary layer conductance (m s⁻¹ LAI⁻¹).
    gs1 : Union[Raster, np.ndarray]
        Stomatal conductance (m s⁻¹ LAI⁻¹).
    Gcu : Union[Raster, np.ndarray]
        Cuticular conductance (m s⁻¹ LAI⁻¹).

    Returns:
    Union[Raster, np.ndarray]
        Canopy conductance (Cc) to water vapor in m s⁻¹. Higher values indicate greater ease of water vapor transfer.

    Notes:
    - Canopy conductance is the inverse of surface resistance (rs) in the Penman-Monteith equation.
    - Integrates physiological (stomatal), anatomical (cuticular), and physical (boundary layer) controls on water flux.
    - Sensitive to environmental stress (drought, humidity, leaf wetness).
    - If LAI or (1 - fwet) is zero, Cc is set to zero (no transpiration).
    - Clipped to a minimum value to avoid unphysical results.

    References:
    Thornton, P. E. (1998). A mechanistic approach to modeling photosynthesis at the leaf and canopy scale. Global Change Biology, 4(4), 389-404.
    Running, S. W., & Kimball, J. S. (2005). Remote Sensing of Terrestrial Ecosystem Processes: A Review of MODIS Algorithms. Remote Sensing of Environment, 92(1), 1-19.
    Monteith, J. L., & Unsworth, M. H. (2001). Principles of Environmental Physics (3rd ed.). Academic Press.
    Jarvis, P. G., & McNaughton, K. G. (1986). Stomatal control of transpiration: Scaling up from leaf to region. Advances in Ecological Research, 15, 1-49.

    Example:
        >>> import numpy as np
        >>> LAI = np.array([2.0, 3.0])
        >>> fwet = np.array([0.1, 0.2])
        >>> gl_sh = np.array([0.02, 0.03])
        >>> gs1 = np.array([0.15, 0.12])
        >>> Gcu = np.array([0.01, 0.01])
        >>> Cc = calculate_canopy_conductance(LAI, fwet, gl_sh, gs1, Gcu)
        >>> print(Cc)
    """
    
    # Only compute conductance where there is leaf area and the surface is not fully wet
    Cc = rt.where(
        np.logical_and(LAI > 0.0, (1.0 - fwet) > 0.0),
        # Series-parallel conductance: stomatal and cuticular conductances in parallel, in series with boundary layer
        gl_sh * (gs1 + Gcu) / (gs1 + gl_sh + Gcu) * LAI * (1.0 - fwet),
        # If no leaf area or surface is fully wet, set conductance to zero (no transpiration)
        0.0
    )

    # Clip conductance to a minimum value to avoid unphysical/extreme results
    Cc = rt.clip(Cc, 1.0 / MAX_RESISTANCE, None)

    # Return canopy conductance (m s^-1)
    return Cc
