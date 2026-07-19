import pandas as pd
import numpy as np
from src.features.feature_engineering import FeatureEngineer

def test_feature_engineer_trig_and_dist():
    df = pd.DataFrame({'x': [1.0, 0.0], 'y': [0.0, 1.0]})
    eng = FeatureEngineer()
    eng.use_trigonometric = True
    eng.use_distance = True
    
    df_out = eng.transform(df)
    
    assert 'sin_x' in df_out.columns
    assert 'r' in df_out.columns
    assert np.isclose(df_out['r'].iloc[0], 1.0)
    assert np.isclose(df_out['r'].iloc[1], 1.0)
    assert np.isclose(df_out['sin_x'].iloc[1], 0.0)
