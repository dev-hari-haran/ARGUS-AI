import pandas as pd
from typing import List, Tuple
from sklearn.preprocessing import StandardScaler
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

class DataScaler:
    def __init__(self, feature_cols: List[str], target_cols: List[str]):
        """
        Initializes scalers for features and targets.
        """
        self.feature_cols = feature_cols
        self.target_cols = target_cols
        self.feature_scaler = StandardScaler()
        self.target_scaler = StandardScaler()
        self._is_fitted = False
        
    def fit(self, train_df: pd.DataFrame):
        """
        Fits the scalers only on the training set to prevent data leakage.
        """
        logger.info("Fitting scalers on training set...")
        self.feature_scaler.fit(train_df[self.feature_cols])
        self.target_scaler.fit(train_df[self.target_cols])
        self._is_fitted = True
        
    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Transforms features and targets using fitted scalers.
        """
        if not self._is_fitted:
            raise ValueError("Scalers must be fitted before calling transform!")
            
        X = pd.DataFrame(
            self.feature_scaler.transform(df[self.feature_cols]),
            columns=self.feature_cols,
            index=df.index
        )
        
        y = pd.DataFrame(
            self.target_scaler.transform(df[self.target_cols]),
            columns=self.target_cols,
            index=df.index
        )
        
        return X, y
        
    def inverse_transform_targets(self, y_scaled: pd.DataFrame) -> pd.DataFrame:
        """
        Inverses the target scaling to retrieve original units.
        """
        return pd.DataFrame(
            self.target_scaler.inverse_transform(y_scaled),
            columns=self.target_cols,
            index=y_scaled.index
        )
