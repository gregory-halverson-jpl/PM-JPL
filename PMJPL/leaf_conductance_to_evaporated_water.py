from .PMJPL_parameter_from_IGBP import PMJPL_parameter_from_IGBP
from rasters import Raster, RasterGeometry, VectorGeometry
from typing import Union

def leaf_conductance_to_evaporated_water(IGBP: Union[Raster, int], geometry=None, IGBP_upsampling_resolution_meters=None):
    return PMJPL_parameter_from_IGBP(
        variable="gl_e_wv",
        IGBP=IGBP,
        geometry=geometry,
        IGBP_upsampling_resolution_meters=IGBP_upsampling_resolution_meters
    )
