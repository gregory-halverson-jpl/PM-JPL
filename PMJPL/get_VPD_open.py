from .PMJPL_parameter_from_IGBP import PMJPL_parameter_from_IGBP
from rasters import Raster, RasterGeometry, VectorGeometry
from typing import Union

def get_VPD_open(IGBP: Union[Raster, int], geometry=None, IGBP_upsampling_resolution_meters=None):
    return PMJPL_parameter_from_IGBP(
        variable="vpd_open",
        IGBP=IGBP,
        geometry=geometry,
        IGBP_upsampling_resolution_meters=IGBP_upsampling_resolution_meters
    )
