#!/usr/bin/env python3
"""
Simple test script for the generate_PMJPL_inputs function
"""

import pandas as pd
import numpy as np
from datetime import datetime

def test_generate_PMJPL_inputs():
    """Test the generate_PMJPL_inputs function with sample data"""
    
    # Import the function
    from PMJPL.generate_PMJPL_inputs import generate_PMJPL_inputs
    
    # Create a sample input DataFrame
    sample_data = {
        'tower': ['US-Var', 'US-ARM'],
        'lat': [38.4133, 36.6058],
        'lon': [-120.9508, -97.4888],
        'time_UTC': ['2020-06-15 12:00:00', '2020-06-15 12:00:00'],
        'albedo': [0.15, 0.18],
        'elevation_km': [0.129, 0.314],
        'IGBP': [1, 10]  # 1=Evergreen Needleleaf Forest, 10=Grasslands
    }
    
    input_df = pd.DataFrame(sample_data)
    
    print("Input DataFrame:")
    print(input_df)
    print("\n" + "="*60 + "\n")
    
    # Generate PMJPL inputs
    result_df = generate_PMJPL_inputs(input_df)
    
    print("Result DataFrame:")
    print(result_df)
    print("\n" + "="*60 + "\n")
    
    # Check that all expected columns are present
    expected_columns = [
        'tower', 'lat', 'lon', 'time_UTC', 'albedo', 'elevation_km', 'IGBP',
        'hour_of_day', 'doy', 'gl_sh', 'gl_e_wv', 'RBL_min', 'RBL_max', 
        'CL', 'Tmin_open', 'Tmin_closed', 'VPD_closed', 'VPD_open'
    ]
    
    print("Column check:")
    for col in expected_columns:
        if col in result_df.columns:
            print(f"✓ {col}: {result_df[col].iloc[0]}")
        else:
            print(f"✗ {col}: MISSING")
    
    print(f"\nTotal columns: {len(result_df.columns)}")
    print(f"Expected columns: {len(expected_columns)}")
    
    return result_df

if __name__ == "__main__":
    result = test_generate_PMJPL_inputs()
