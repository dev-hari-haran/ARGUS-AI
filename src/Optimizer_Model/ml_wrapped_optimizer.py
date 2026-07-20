import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from src.Optimizer_Model.optimized_model import OptimizedModel
from src.utils.paths import MODELS_DIR

class MLWrappedOptimizer:
    def __init__(self, solver='lm'):
        """
        Wraps OptimizedModel to transparently handle scaling/unscaling
        so it behaves identically to sklearn/ML models.
        """
        self.model = OptimizedModel(solver)
        self.scaler = None
        
    def fit(self, X_train, y_train):
        """
        Loads the scaler from disk to handle inverse transforms during predict.
        """
        scaler_path = MODELS_DIR / "scaler.pkl"
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
        else:
            raise FileNotFoundError("scaler.pkl must exist in models directory before fitting MLWrappedOptimizer.")
            
        return self
        
    def predict(self, X_scaled: pd.DataFrame) -> np.ndarray:
        if self.scaler is None:
            raise ValueError("Model must be fitted to acquire the scaler.")
            
        # 1. Unscale features to get physical 'x', 'y', 'l1', 'l2'
        X_unscaled_arr = self.scaler.feature_scaler.inverse_transform(X_scaled)
        X_unscaled = pd.DataFrame(X_unscaled_arr, columns=self.scaler.feature_cols, index=X_scaled.index)
        
        # 2. Predict physical joint angles
        q_unscaled_arr = self.model.predict(X_unscaled)
        q_unscaled = pd.DataFrame(q_unscaled_arr, columns=self.scaler.target_cols, index=X_scaled.index)
        
        # 3. Transform predictions back to scaled space
        q_scaled_arr = self.scaler.target_scaler.transform(q_unscaled)
        return q_scaled_arr
