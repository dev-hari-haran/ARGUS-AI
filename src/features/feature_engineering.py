import numpy as np
import pandas as pd
from src.utils.config_loader import load_config

class FeatureEngineer:
    def __init__(self):
        config = load_config('features')
        self.use_trigonometric = config.get('use_trigonometric', True)
        self.use_distance = config.get('use_distance', True)
        
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies feature engineering based on the configuration.
        Assumes 'x', 'y', 'l1', and 'l2' columns are present in the DataFrame.
        """
        df_out = df.copy()
        
        if self.use_trigonometric:
            # Base angle theta (atan2)
            df_out['theta_base'] = np.arctan2(df_out['y'], df_out['x'])
            
            # Cosine rule term for theta2: (x^2 + y^2 - L1^2 - L2^2) / (2*L1*L2)
            # Clip between -1 and 1 to prevent arccos domain errors
            c2 = (df_out['x']**2 + df_out['y']**2 - df_out['l1']**2 - df_out['l2']**2) / (2 * df_out['l1'] * df_out['l2'])
            df_out['cosine_term'] = np.clip(c2, -1.0, 1.0)
            
        if self.use_distance:
            # Radius (distance from origin)
            df_out['r'] = np.sqrt(df_out['x']**2 + df_out['y']**2)
            
        return df_out
