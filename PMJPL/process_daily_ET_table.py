import pandas as pd

from sun_angles import SHA_deg_from_DOY_lat, daylight_from_SHA, sunrise_from_SHA
from verma_net_radiation import daily_Rn_integration_verma
from daily_evapotranspiration_upscaling import daily_ET_from_daily_LE

from .meteorology_conversion.meteorology_conversion import celcius_to_kelvin

def process_daily_ET_table(input_df: pd.DataFrame) -> pd.DataFrame:
    hour_of_day = input_df.hour_of_day
    DOY = input_df.doy
    lat = input_df.lat
    LE = input_df.LE
    Rn = input_df.Rn
    EF = LE / Rn

    SHA_deg = SHA_deg_from_DOY_lat(DOY=DOY, latitude=lat)
    sunrise_hour = sunrise_from_SHA(SHA_deg)
    daylight_hours = daylight_from_SHA(SHA_deg)

    Rn_daylight = daily_Rn_integration_verma(
        Rn=Rn,
        hour_of_day=hour_of_day,
        DOY=DOY,
        lat=lat,
        sunrise_hour=sunrise_hour,
        daylight_hours=daylight_hours
    )

    LE_daylight = EF * Rn_daylight
    ET = daily_ET_from_daily_LE(LE_daylight, daylight_hours)

    output_df = input_df.copy()
    output_df["EF"] = EF
    output_df["sunrise_hour"] = sunrise_hour
    output_df["daylight_hours"] = daylight_hours
    output_df["Rn_daylight"] = Rn_daylight
    output_df["ET"] = ET

    return output_df
