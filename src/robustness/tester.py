import numpy as np
import pandas as pd
from pathlib import Path
from src.utils.logging_utils import get_logger
from src.evaluation.metrics import evaluate_predictions
from src.kinematics.workspace import Workspace

class RobustnessTester:
    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler
        self.logger = get_logger(self.__class__.__name__)
        self.ws = Workspace()
        
    def test_with_noise(self, X_test: pd.DataFrame, y_test: pd.DataFrame, noise_level: float = 0.01) -> dict:
        """
        Adds Gaussian noise to the scaled features and evaluates the model.
        """
        self.logger.info(f"Testing robustness with {noise_level} Gaussian noise...")
        X_test_noisy = X_test + np.random.normal(0, noise_level, X_test.shape)
        
        preds_scaled = self.model.predict(X_test_noisy)
        # Handle models returning arrays instead of DataFrames
        if len(preds_scaled.shape) == 1:
            preds_scaled = preds_scaled.reshape(1, -1)
        preds_df = pd.DataFrame(preds_scaled, columns=['q1', 'q2'], index=X_test.index)
        
        preds = self.scaler.inverse_transform_targets(preds_df)
        y_true = self.scaler.inverse_transform_targets(y_test)
        
        # Get unscaled L1 and L2
        X_test_unscaled = pd.DataFrame(
            self.scaler.feature_scaler.inverse_transform(X_test),
            columns=self.scaler.feature_cols,
            index=X_test.index
        )
        l1_vals = X_test_unscaled['l1'].values
        l2_vals = X_test_unscaled['l2'].values
        
        metrics = evaluate_predictions(y_true, preds, l1_vals, l2_vals)
        return metrics
        
    def test_near_singularities(self, X_test: pd.DataFrame, y_test: pd.DataFrame, threshold: float = 0.1) -> dict:
        """
        Tests the model near singularities (where q2 is close to 0).
        """
        self.logger.info("Testing robustness near singularities...")
        
        y_true = self.scaler.inverse_transform_targets(y_test)
        # Find indices where q2 is near 0
        mask = np.abs(y_true['q2']) < threshold
        
        if mask.sum() == 0:
            self.logger.warning("No samples found near singularity in the provided set.")
            return {}
            
        X_sing = X_test[mask]
        y_sing = y_test[mask]
        
        preds_scaled = self.model.predict(X_sing)
        if len(preds_scaled.shape) == 1:
            preds_scaled = preds_scaled.reshape(1, -1)
        preds_df = pd.DataFrame(preds_scaled, columns=['q1', 'q2'], index=X_sing.index)
        
        preds = self.scaler.inverse_transform_targets(preds_df)
        y_true_sing = self.scaler.inverse_transform_targets(y_sing)
        
        # Get unscaled L1 and L2
        X_test_unscaled = pd.DataFrame(
            self.scaler.feature_scaler.inverse_transform(X_sing),
            columns=self.scaler.feature_cols,
            index=X_sing.index
        )
        l1_vals = X_test_unscaled['l1'].values
        l2_vals = X_test_unscaled['l2'].values
        
        metrics = evaluate_predictions(y_true_sing, preds, l1_vals, l2_vals)
        return metrics
