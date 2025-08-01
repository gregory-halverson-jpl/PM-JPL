"""
MOD16 model of evapotranspiration

This implementation follows the MOD16 Version 1.5 Collection 6 algorithm described in the MOD16 user's guide.
https://landweb.nascom.nasa.gov/QA_WWW/forPage/user_guide/MOD16UsersGuide2016.pdf

Developed by Gregory Halverson in the Jet Propulsion Laboratory Year-Round Internship Program (Columbus Technologies and Services), in coordination with the ECOSTRESS mission and master's thesis studies at California State University, Northridge.
"""
import logging
from typing import Dict, Union
from datetime import datetime

import numpy as np
import rasters as rt
from rasters import Raster, RasterGrid, RasterGeometry

from check_distribution import check_distribution
from GEOS5FP import GEOS5FP
from NASADEM import NASADEM
from verma_net_radiation import verma_net_radiation
from SEBAL_soil_heat_flux import calculate_SEBAL_soil_heat_flux
from MCD12C1_2019_v006 import load_MCD12C1_IGBP

from carlson_fractional_vegetation_cover import carlson_fractional_vegetation_cover
from carlson_leaf_area_index import carlson_leaf_area_index

from daily_evapotranspiration_upscaling import lambda_Jkg_from_Ta_C

from meteorology_conversion import SVP_Pa_from_Ta_C
from meteorology_conversion import calculate_air_density
from meteorology_conversion import calculate_specific_heat
from meteorology_conversion import calculate_specific_humidity
from meteorology_conversion import calculate_surface_pressure
from meteorology_conversion import celcius_to_kelvin

from priestley_taylor import delta_Pa_from_Ta_C

from .parameters import MOD16_parameter_from_IGBP

from .calculate_gamma import calculate_gamma

from carlson_leaf_area_index import carlson_leaf_area_index
from .constants import *

from .fwet import calculate_fwet
from .soil_moisture_constraint import calculate_fSM
from .tmin_factor import calculate_tmin_factor
from .correctance_factor import calculate_rcorr
from .VPD_factor import calculate_VPD_factor

from .canopy_conductance import calculate_canopy_conductance

from .wet_canopy_resistance import calculate_wet_canopy_resistance
from .canopy_aerodynamic_resistance import calculate_canopy_aerodynamic_resistance

from .wet_soil_evaporation import calculate_wet_soil_evaporation
from .potential_soil_evaporation import calculate_potential_soil_evaporation
from .interception import calculate_interception
from .transpiration import calculate_transpiration

__author__ = 'Qiaozhen Mu, Maosheng Zhao, Steven W. Running, Gregory Halverson'

logger = logging.getLogger(__name__)

DEFAULT_WORKING_DIRECTORY = "."
DEFAULT_MOD16_INTERMEDIATE = "MOD16_intermediate"

DEFAULT_OUTPUT_VARIABLES = [
    'LEi',
    'LEc',
    'LEs',
    'LE',
    'LE_daily',
    'ET_daily_kg'
]


def PMJPL(
        NDVI: Union[Raster, np.ndarray],
        ST_C: Union[Raster, np.ndarray] = None,
        emissivity: Union[Raster, np.ndarray] = None,
        albedo: Union[Raster, np.ndarray] = None,
        Rn: Union[Raster, np.ndarray] = None,
        G: Union[Raster, np.ndarray] = None,
        Ta_C: Union[Raster, np.ndarray] = None,
        Tmin_C: Union[Raster, np.ndarray] = None,
        RH: Union[Raster, np.ndarray] = None,
        IGBP: Union[Raster, np.ndarray] = None,
        FVC: Union[Raster, np.ndarray] = None,
        geometry: RasterGeometry = None,
        time_UTC: datetime = None,
        GEOS5FP_connection: GEOS5FP = None,
        resampling: str = "nearest",
        Ps_Pa: Union[Raster, np.ndarray] = None,
        elevation_km: Union[Raster, np.ndarray] = None,
        delta_Pa: Union[Raster, np.ndarray] = None,
        lambda_Jkg: Union[Raster, np.ndarray] = None,
        gamma_Jkg: Union[Raster, np.ndarray, float] = None) -> Dict[str, Raster]:
    results = {}

    if geometry is None and isinstance(NDVI, Raster):
        geometry = NDVI.geometry

    if GEOS5FP_connection is None:
        GEOS5FP_connection = GEOS5FP()

    if Ta_C is None and geometry is not None and time_UTC is not None:
        Ta_C = GEOS5FP_connection.Ta_C(
            time_UTC=time_UTC,
            geometry=geometry,
            resampling=resampling
        )

    if Ta_C is None:
        raise ValueError("air temperature (Ta_C) not given")

    if Tmin_C is None and geometry is not None and time_UTC is not None:
        Tmin_K = GEOS5FP_connection.Tmin_K(
            time_UTC=time_UTC,
            geometry=geometry,
            resampling=resampling
        )

        Tmin_C = Tmin_K - 273.15

    if Tmin_C is None:
        raise ValueError("minimum temperature (Tmin_C) not given")

    if RH is None and geometry is not None and time_UTC is not None:
        RH = GEOS5FP_connection.RH(
            time_UTC=time_UTC,
            geometry=geometry,
            resampling=resampling
        )

    if RH is None:
        raise ValueError("relative humidity (RH) not given")

    if elevation_km is None and geometry is not None:
        elevation_km = NASADEM.elevation_km(geometry=geometry)

    elevation_m = elevation_km * 1000.0

    if IGBP is None and geometry is not None:
        IGBP = load_MCD12C1_IGBP(geometry=geometry)

    if Rn is None and albedo is not None and ST_C is not None and emissivity is not None:
        if SWin is None and geometry is not None and time_UTC is not None:
            SWin = GEOS5FP_connection.SWin(
                time_UTC=time_UTC,
                geometry=geometry,
                resampling=resampling
            )

        Rn_results = verma_net_radiation(
            SWin=SWin,
            albedo=albedo,
            ST_C=ST_C,
            emissivity=emissivity,
            Ta_C=Ta_C,
            RH=RH
        )

        Rn = Rn_results["Rn"]

    if Rn is None:
        raise ValueError("net radiation (Rn) not given")

    if G is None and Rn is not None and ST_C is not None and NDVI is not None and albedo is not None:
        G = calculate_SEBAL_soil_heat_flux(
            Rn=Rn,
            ST_C=ST_C,
            NDVI=NDVI,
            albedo=albedo
        )

    if G is None:
        raise ValueError("soil heat flux (G) not given")
    
    results["G"] = G

    LAI = carlson_leaf_area_index(NDVI)

    # calculate fraction of vegetation cover if it's not given
    if FVC is None:
        # calculate fraction of vegetation cover from NDVI
        FVC = carlson_fractional_vegetation_cover(NDVI)

    # calculate surface air pressure if it's not given
    if Ps_Pa is None:
        # calculate surface air pressure is Pascal
        Ps_Pa = calculate_surface_pressure(elevation_m=elevation_m, Ta_C=Ta_C)

    # calculate Penman-Monteith/Priestley-Taylor delta term if it's not given
    if delta_Pa is None:
        # calculate Penman-Monteith/Priestley-Taylor delta term in Pascal per degree Celsius
        delta_Pa = delta_Pa_from_Ta_C(Ta_C)

    # calculate latent heat of vaporization if it's not given
    if lambda_Jkg is None:
        # calculate latent heat of vaporization in Joules per kilogram
        lambda_Jkg = lambda_Jkg_from_Ta_C(Ta_C)

    logger.info("calculating PM-MOD meteorology")

    # calculate air temperature in Kelvin
    Ta_K = celcius_to_kelvin(Ta_C)

    # calculate saturation vapor pressure in Pascal from air temperature in Celsius
    SVP_Pa = SVP_Pa_from_Ta_C(Ta_C)

    # calculate vapor pressure in Pascal from releative humidity and saturation vapor pressure
    Ea_Pa = RH * SVP_Pa

    # specific humidity of air
    # as a ratio of kilograms of water to kilograms of air and water
    # from surface pressure and actual water vapor pressure
    specific_humidity = calculate_specific_humidity(Ea_Pa, Ps_Pa)
    results['specific_humidity'] = specific_humidity

    # calculate air density (rho) in kilograms per cubic meter
    rho_kgm3 = calculate_air_density(Ps_Pa, Ta_K, specific_humidity)
    results["rho_kgm3"] = rho_kgm3

    # calculate specific heat capacity of the air (Cp)
    # in joules per kilogram per kelvin
    # from specific heat of water vapor (CPW)
    # and specific heat of dry air (CPD)
    Cp_Jkg = calculate_specific_heat(specific_humidity)
    results["Cp"] = Cp_Jkg

    # calculate delta term if it's not given
    if delta_Pa is None:
        # slope of saturation vapor pressure curve in Pascal per degree
        delta_Pa = delta_Pa_from_Ta_C(Ta_C)

    results["delta_Pa"] = delta_Pa

    # calculate gamma term if it's not given
    if gamma_Jkg is None:
        # calculate psychrometric gamma in Joules per kilogram
        gamma_Jkg = calculate_gamma(
            Ta_C=Ta_C,
            Ps_Pa=Ps_Pa,
            Cp_Jkg=Cp_Jkg
        )

    # vapor pressure deficit in Pascal
    VPD_Pa = rt.clip(SVP_Pa - Ea_Pa, 0.0, None)

    # calculate relative surface wetness (fwet)
    # from relative humidity
    fwet = calculate_fwet(RH)
    results['fwet'] = fwet

    logger.info("calculating PM-MOD resistances")

    # query leaf conductance to sensible heat (gl_sh) in seconds per meter
    gl_sh = MOD16_parameter_from_IGBP(
        variable="gl_sh",
        IGBP=IGBP
    )

    results['gl_sh'] = gl_sh

    # calculate wet canopy resistance to sensible heat (rhc) in seconds per meter
    # from leaf conductance to sensible heat (gl_sh), LAI, and relative surface wetness (fwet)
    rhc = calculate_wet_canopy_resistance(gl_sh, LAI, fwet)
    results['rhc'] = rhc

    # calculate resistance to radiative heat transfer through air (rrc)
    rrc = np.float32(rho_kgm3 * Cp_Jkg / (4.0 * SIGMA * Ta_K ** 3.0))
    results['rrc'] = rrc

    # calculate aerodynamic resistance (rhrc)
    # in seconds per meter
    # from wet canopy resistance to sensible heat
    # and resistance to radiative heat transfer through air
    rhrc = np.float32((rhc * rrc) / (rhc + rrc))
    results['rhrc'] = rhrc

    # calculate leaf conductance to evaporated water vapor (gl_e_wv)
    gl_e_wv = MOD16_parameter_from_IGBP(
        variable="gl_e_wv",
        IGBP=IGBP
    )

    results['gl_e_wv'] = gl_e_wv

    rvc = calculate_wet_canopy_resistance(gl_e_wv, LAI, fwet)
    results['rvc'] = rvc

    # caluclate available radiation to the canopy (Ac)
    # in watts per square meter
    # this is the same as net radiation to the canopy in PT-JPL
    Ac = Rn * FVC
    results['Ac'] = Ac

    # calculate wet latent heat flux (LEi)
    # in watts per square meter
    LEi = calculate_interception(
        delta_Pa=delta_Pa,
        Ac=Ac,
        rho=rho_kgm3,
        Cp=Cp_Jkg,
        VPD_Pa=VPD_Pa,
        FVC=FVC,
        rhrc=rhrc,
        fwet=fwet,
        rvc=rvc,
        # gamma_Jkg=gamma_Jkg
    )

    results['LEi'] = LEi

    # calculate correctance factor (rcorr)
    # for stomatal and cuticular conductances
    # from surface pressure and air temperature
    rcorr = calculate_rcorr(Ps_Pa, Ta_K)
    results['rcorr'] = rcorr

    # query biome-specific mean potential stomatal conductance per unit leaf area
    CL = MOD16_parameter_from_IGBP(
        variable="cl",
        IGBP=IGBP
    )

    results['CL'] = CL

    # query open minimum temperature by land-cover
    tmin_open = MOD16_parameter_from_IGBP(
        variable="tmin_open",
        IGBP=IGBP
    )

    results['tmin_open'] = tmin_open

    # query closed minimum temperature by land-cover
    tmin_close = MOD16_parameter_from_IGBP(
        variable="tmin_close",
        IGBP=IGBP
    )

    results['tmin_close'] = tmin_close

    check_distribution(Tmin_C, "Tmin_C")
    check_distribution(tmin_open, "tmin_open")
    check_distribution(tmin_close, "tmin_close")

    # calculate minimum temperature factor for stomatal conductance
    mTmin = calculate_tmin_factor(Tmin_C, tmin_open, tmin_close)
    results['mTmin'] = mTmin

    # query open vapor pressure deficit by land-cover
    VPD_open = MOD16_parameter_from_IGBP(
        variable="vpd_open",
        IGBP=IGBP
    )

    results['vpd_open'] = VPD_open

    # query closed vapor pressure deficit by land-cover
    VPD_close = MOD16_parameter_from_IGBP(
        variable="vpd_close",
        IGBP=IGBP
    )

    results['vpd_close'] = VPD_close

    # calculate vapor pressure deficit factor for stomatal conductance
    mVPD = calculate_VPD_factor(VPD_open, VPD_close, VPD_Pa)
    results['mVPD'] = mVPD

    # calculate stomatal conductance (gs1)
    gs1 = CL * mTmin * mVPD * rcorr
    results['gs1'] = gs1

    # correct cuticular conductance constant to leaf cuticular conductance (Gcu) using correction factor (rcorr)
    Gcu = CUTICULAR_CONDUCTANCE * rcorr
    results['Gcu'] = Gcu

    # calculate canopy conductance
    # equivalent to g_canopy
    Cc = calculate_canopy_conductance(LAI, fwet, gl_sh, gs1, Gcu)
    results['Cc'] = Cc

    # calculate surface resistance to evapotranspiration as inverse of canopy conductance (Cc)
    rs = rt.clip(1.0 / Cc, 0.0, MAX_RESISTANCE)
    results['rs'] = rs

    # calculate convective heat transfer as inverse of leaf conductance to sensible heat (gl_sh)
    rh = 1.0 / gl_sh
    results['rh'] = rs

    # calculate radiative heat transfer (rr)
    rr = rho_kgm3 * Cp_Jkg / (4.0 * SIGMA * Ta_K ** 3)
    results['rr'] = rr

    # calculate parallel resistance (ra)
    # MOD16 user guide is not clear about what to call this
    ra = (rh * rr) / (rh + rr)
    results["ra"] = ra

    # calculate transpiration
    LEc = calculate_transpiration(
        delta_Pa=delta_Pa,
        Ac=Ac,
        rho_kgm3=rho_kgm3,
        Cp_Jkg=Cp_Jkg,
        VPD_Pa=VPD_Pa,
        FVC=FVC,
        ra=ra,
        fwet=fwet,
        rs=rs,
        # gamma_Jkg=gamma_Jkg
    )

    results['LEc'] = LEc

    # soil evaporation

    # query aerodynamic resistant constraints from land-cover
    RBL_max = MOD16_parameter_from_IGBP(
        variable="rbl_max",
        IGBP=IGBP
    )

    results['rbl_max'] = RBL_max

    RBL_min = MOD16_parameter_from_IGBP(
        variable="rbl_min",
        IGBP=IGBP
    )

    results['rbl_min'] = RBL_min

    # calculate canopy aerodynamic resistance in seconds per meter
    rtotc = calculate_canopy_aerodynamic_resistance(VPD_Pa, VPD_open, VPD_close, RBL_max, RBL_min)
    results['rtotc'] = rtotc

    # calculate total aerodynamic resistance
    # by applying correction to total canopy resistance
    rtot = rcorr * rtotc
    results['rtot'] = rtot

    # calculate resistance to radiative heat transfer through air
    rrs = np.float32(rho_kgm3 * Cp_Jkg / (4.0 * SIGMA * Ta_K ** 3))
    results['rrs'] = rrs

    # calculate aerodynamic resistance at the soil surface
    ras = (rtot * rrs) / (rtot + rrs)
    results['ras'] = ras

    # calculate available radiation at the soil
    Asoil = rt.clip((1.0 - FVC) * Rn - G, 0.0, None)
    results['Asoil'] = Asoil

    # separate wet soil evaporation and potential soil evaporation

    # calculate wet soil evaporation
    LE_soil_wet = calculate_wet_soil_evaporation(
        delta_Pa=delta_Pa,
        Asoil=Asoil,
        rho_kgm3=rho_kgm3,
        Cp_Jkg=Cp_Jkg,
        FVC=FVC,
        VPD_Pa=VPD_Pa,
        ras=ras,
        fwet=fwet,
        rtot=rtot,
        # gamma_Jkg=gamma_Jkg
    )

    results['LE_soil_wet'] = LE_soil_wet

    # calculate potential soil evaporation
    LE_soil_pot = calculate_potential_soil_evaporation(
        delta_Pa=delta_Pa,
        Asoil=Asoil,
        rho=rho_kgm3,
        Cp_Jkg=Cp_Jkg,
        FVC=FVC,
        VPD_Pa=VPD_Pa,
        ras=ras,
        fwet=fwet,
        rtot=rtot,
        # gamma_Jkg=gamma_Jkg
    )

    results['LE_soil_pot'] = LE_soil_pot

    # calculate soil moisture constraint
    fSM = calculate_fSM(RH, VPD_Pa)
    results['fSM'] = fSM

    # calculate soil evaporation
    LEs = rt.clip(LE_soil_wet + LE_soil_pot * fSM, 0.0, None)

    # fill soil evaporation with zero
    LEs = rt.where(np.isnan(LEs), 0.0, LEs)
    results['LEs'] = LEs

    # sum partitions into total latent heat flux
    LE = rt.clip(LEi + LEc + LEs, 0.0, Rn)
    results['LE'] = LE

    return results
