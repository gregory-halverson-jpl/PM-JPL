"""
Module: generate_PMJPL_inputs.py
-------------------------------
This module provides a function to generate the required input DataFrame for the PM-JPL model. It processes a calibration/validation DataFrame, computes additional variables such as hour of day, day of year (doy), and loads static parameters from the MOD16 lookup table based on IGBP land cover classification. The function is robust to missing or problematic data, logging warnings and filling with NaN as needed.
"""
import logging

import numpy as np
import pandas as pd
import rasters as rt
from dateutil import parser
from pandas import DataFrame
from solar_apparent_time import UTC_to_solar

from .leaf_conductance_to_sensible_heat import leaf_conductance_to_sensible_heat
from .leaf_conductance_to_evaporated_water import leaf_conductance_to_evaporated_water
from .maximum_boundary_layer_resistance import maximum_boundary_layer_resistance
from .minimum_boundary_layer_resistance import minimum_boundary_layer_resistance
from .potential_stomatal_conductance import potential_stomatal_conductance
from .open_minimum_temperature import open_minimum_temperature
from .closed_minimum_temperature import closed_minimum_temperature
from .open_vapor_pressure_deficit import open_vapor_pressure_deficit
from .closed_vapor_pressure_deficit import closed_vapor_pressure_deficit
from .model import PMJPL

logger = logging.getLogger(__name__)

# FIXME include additional inputs required by PM-JPL that were not required by previous models

def generate_PMJPL_inputs(PMJPL_inputs_from_calval_df: DataFrame) -> DataFrame:
    """
    Generate a DataFrame with all required inputs for the PM-JPL model.

    Parameters
    ----------
    PMJPL_inputs_from_calval_df : pandas.DataFrame
        DataFrame containing the columns: tower, lat, lon, time_UTC, albedo, elevation_km, IGBP

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the original columns plus:
        - hour_of_day: int, hour of solar time at the site
        - doy: int, day of year
        - gl_sh: float, leaf conductance to sensible heat per unit LAI (m s-1 LAI-1)
        - gl_e_wv: float, leaf conductance to evaporated water per unit LAI (m s-1 LAI-1)
        - RBL_min: float, minimum atmospheric boundary layer resistance (s m-1)
        - RBL_max: float, maximum atmospheric boundary layer resistance (s m-1)
        - CL: float, mean potential stomatal conductance per unit leaf area (m s-1)
        - Tmin_open: float, temperature at which stomata are completely open (deg C)
        - Tmin_closed: float, temperature at which stomata are almost completely closed (deg C)
        - VPD_closed: float, VPD at which stomata are almost completely closed (Pa)
        - VPD_open: float, VPD at which stomata are completely open (Pa)

    Notes
    -----
    - This function is robust to missing or problematic data; missing values are filled with np.nan.
    - The function logs progress and warnings for traceability.
    - If columns already exist in the input DataFrame, they are not overwritten.
    - Static parameters are loaded from the MOD16 lookup table based on IGBP land cover classification.
    """
    # Copy input DataFrame to avoid modifying the original
    PMJPL_inputs_df = PMJPL_inputs_from_calval_df.copy()

    # Prepare lists to collect computed values
    hour_of_day = []
    doy = []

    # Iterate over each row to compute additional variables
    for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
        tower = input_row.tower
        lat = input_row.lat
        lon = input_row.lon
        time_UTC = input_row.time_UTC
        albedo = input_row.albedo
        elevation_km = input_row.elevation_km
        IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
        
        logger.info(f"collecting PMJPL inputs for tower {tower} lat {lat} lon {lon} time {time_UTC} UTC IGBP {IGBP}")
        
        # Parse time and convert to solar time
        time_UTC = parser.parse(str(time_UTC))
        time_solar = UTC_to_solar(time_UTC, lon)
        hour_of_day.append(time_solar.hour)
        doy.append(time_UTC.timetuple().tm_yday)
    
    # Add computed columns to DataFrame if not already present
    if not "hour_of_day" in PMJPL_inputs_df.columns:
        PMJPL_inputs_df["hour_of_day"] = hour_of_day

    if not "doy" in PMJPL_inputs_df.columns:
        PMJPL_inputs_df["doy"] = doy
    
    # Load static parameters from MOD16 lookup table based on IGBP
    # Use the same parameter query functions as the model code
    
    # gl_sh: leaf conductance to sensible heat per unit LAI (m s-1 LAI-1)
    if "gl_sh" not in PMJPL_inputs_df.columns:
        try:
            logger.info("loading static parameter gl_sh from MOD16 lookup table")
            gl_sh_values = []
            for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
                IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
                gl_sh_value = leaf_conductance_to_sensible_heat(IGBP=np.array([IGBP]))
                if hasattr(gl_sh_value, '__iter__'):
                    gl_sh_values.append(gl_sh_value[0])
                else:
                    gl_sh_values.append(gl_sh_value)
            PMJPL_inputs_df["gl_sh"] = gl_sh_values
            logger.info("successfully loaded gl_sh")
        except Exception as e:
            logger.exception(f"failed to load parameter gl_sh: {e}")
            PMJPL_inputs_df["gl_sh"] = np.nan

    # gl_e_wv: leaf conductance to evaporated water per unit LAI (m s-1 LAI-1)
    if "gl_e_wv" not in PMJPL_inputs_df.columns:
        try:
            logger.info("loading static parameter gl_e_wv from MOD16 lookup table")
            gl_e_wv_values = []
            for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
                IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
                gl_e_wv_value = leaf_conductance_to_evaporated_water(IGBP=IGBP)
                if hasattr(gl_e_wv_value, '__iter__'):
                    gl_e_wv_values.append(gl_e_wv_value[0])
                else:
                    gl_e_wv_values.append(gl_e_wv_value)
            PMJPL_inputs_df["gl_e_wv"] = gl_e_wv_values
            logger.info("successfully loaded gl_e_wv")
        except Exception as e:
            logger.exception(f"failed to load parameter gl_e_wv: {e}")
            PMJPL_inputs_df["gl_e_wv"] = np.nan

    # RBL_min: minimum atmospheric boundary layer resistance (s m-1)
    if "RBL_min" not in PMJPL_inputs_df.columns:
        try:
            logger.info("loading static parameter RBL_min from MOD16 lookup table")
            RBL_min_values = []
            for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
                IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
                RBL_min_value = minimum_boundary_layer_resistance(IGBP=IGBP)
                if hasattr(RBL_min_value, '__iter__'):
                    RBL_min_values.append(RBL_min_value[0])
                else:
                    RBL_min_values.append(RBL_min_value)
            PMJPL_inputs_df["RBL_min"] = RBL_min_values
            logger.info("successfully loaded RBL_min")
        except Exception as e:
            logger.exception(f"failed to load parameter RBL_min: {e}")
            PMJPL_inputs_df["RBL_min"] = np.nan

    # RBL_max: maximum atmospheric boundary layer resistance (s m-1)
    if "RBL_max" not in PMJPL_inputs_df.columns:
        try:
            logger.info("loading static parameter RBL_max from MOD16 lookup table")
            RBL_max_values = []
            for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
                IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
                RBL_max_value = maximum_boundary_layer_resistance(IGBP=IGBP)
                if hasattr(RBL_max_value, '__iter__'):
                    RBL_max_values.append(RBL_max_value[0])
                else:
                    RBL_max_values.append(RBL_max_value)
            PMJPL_inputs_df["RBL_max"] = RBL_max_values
            logger.info("successfully loaded RBL_max")
        except Exception as e:
            logger.exception(f"failed to load parameter RBL_max: {e}")
            PMJPL_inputs_df["RBL_max"] = np.nan

    # CL: mean potential stomatal conductance per unit leaf area (m s-1)
    if "CL" not in PMJPL_inputs_df.columns:
        try:
            logger.info("loading static parameter CL from MOD16 lookup table")
            CL_values = []
            for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
                IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
                CL_value = potential_stomatal_conductance(IGBP=IGBP)
                if hasattr(CL_value, '__iter__'):
                    CL_values.append(CL_value[0])
                else:
                    CL_values.append(CL_value)
            PMJPL_inputs_df["CL"] = CL_values
            logger.info("successfully loaded CL")
        except Exception as e:
            logger.exception(f"failed to load parameter CL: {e}")
            PMJPL_inputs_df["CL"] = np.nan

    # Tmin_open: temperature at which stomata are completely open (deg C)
    if "Tmin_open" not in PMJPL_inputs_df.columns:
        try:
            logger.info("loading static parameter Tmin_open from MOD16 lookup table")
            Tmin_open_values = []
            for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
                IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
                Tmin_open_value = open_minimum_temperature(IGBP=IGBP)
                if hasattr(Tmin_open_value, '__iter__'):
                    Tmin_open_values.append(Tmin_open_value[0])
                else:
                    Tmin_open_values.append(Tmin_open_value)
            PMJPL_inputs_df["Tmin_open"] = Tmin_open_values
            logger.info("successfully loaded Tmin_open")
        except Exception as e:
            logger.exception(f"failed to load parameter Tmin_open: {e}")
            PMJPL_inputs_df["Tmin_open"] = np.nan

    # Tmin_closed: temperature at which stomata are almost completely closed (deg C)
    if "Tmin_closed" not in PMJPL_inputs_df.columns:
        try:
            logger.info("loading static parameter Tmin_closed from MOD16 lookup table")
            Tmin_closed_values = []
            for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
                IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
                Tmin_closed_value = closed_minimum_temperature(IGBP=IGBP)
                if hasattr(Tmin_closed_value, '__iter__'):
                    Tmin_closed_values.append(Tmin_closed_value[0])
                else:
                    Tmin_closed_values.append(Tmin_closed_value)
            PMJPL_inputs_df["Tmin_closed"] = Tmin_closed_values
            logger.info("successfully loaded Tmin_closed")
        except Exception as e:
            logger.exception(f"failed to load parameter Tmin_closed: {e}")
            PMJPL_inputs_df["Tmin_closed"] = np.nan

    # VPD_closed: VPD at which stomata are almost completely closed (Pa)
    if "VPD_closed" not in PMJPL_inputs_df.columns:
        try:
            logger.info("loading static parameter VPD_closed from MOD16 lookup table")
            VPD_closed_values = []
            for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
                IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
                VPD_closed_value = closed_vapor_pressure_deficit(IGBP=IGBP)
                if hasattr(VPD_closed_value, '__iter__'):
                    VPD_closed_values.append(VPD_closed_value[0])
                else:
                    VPD_closed_values.append(VPD_closed_value)
            PMJPL_inputs_df["VPD_closed"] = VPD_closed_values
            logger.info("successfully loaded VPD_closed")
        except Exception as e:
            logger.exception(f"failed to load parameter VPD_closed: {e}")
            PMJPL_inputs_df["VPD_closed"] = np.nan

    # VPD_open: VPD at which stomata are completely open (Pa)
    if "VPD_open" not in PMJPL_inputs_df.columns:
        try:
            logger.info("loading static parameter VPD_open from MOD16 lookup table")
            VPD_open_values = []
            for i, input_row in PMJPL_inputs_from_calval_df.iterrows():
                IGBP = input_row.IGBP if 'IGBP' in input_row else 1  # Default to evergreen needleleaf forest
                VPD_open_value = open_vapor_pressure_deficit(IGBP=IGBP)
                if hasattr(VPD_open_value, '__iter__'):
                    VPD_open_values.append(VPD_open_value[0])
                else:
                    VPD_open_values.append(VPD_open_value)
            PMJPL_inputs_df["VPD_open"] = VPD_open_values
            logger.info("successfully loaded VPD_open")
        except Exception as e:
            logger.exception(f"failed to load parameter VPD_open: {e}")
            PMJPL_inputs_df["VPD_open"] = np.nan
    
    # Rename temperature column if needed for model compatibility
    if "Ta" in PMJPL_inputs_df and "Ta_C" not in PMJPL_inputs_df:
        PMJPL_inputs_df.rename({"Ta": "Ta_C"}, inplace=True)
    
    return PMJPL_inputs_df
