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
        Assumes 'x' and 'y' columns are present in the DataFrame.
        """
        df_out = df.copy()
        
        if self.use_trigonometric:
            df_out['sin_x'] = np.sin(df_out['x'])
            df_out['cos_x'] = np.cos(df_out['x'])
            df_out['sin_y'] = np.sin(df_out['y'])
            df_out['cos_y'] = np.cos(df_out['y'])
            
        if self.use_distance:
            df_out['r'] = np.sqrt(df_out['x']**2 + df_out['y']**2)
            
        return df_out
