from .PMJPL_parameter_from_IGBP import PMJPL_parameter_from_IGBP
from rasters import Raster, RasterGeometry, VectorGeometry
from typing import Union

def closed_minimum_temperature(IGBP: Union[Raster, int], geometry=None, IGBP_upsampling_resolution_meters=None):
    return PMJPL_parameter_from_IGBP(
        variable="Tmin_closed",
        IGBP=IGBP,
        geometry=geometry,
        IGBP_upsampling_resolution_meters=IGBP_upsampling_resolution_meters
    )
