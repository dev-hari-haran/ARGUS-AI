import numpy as np
import pandas as pd
from .damped_least_squares import DampedLeastSquares
from .levenberg_marquardt import LevenbergMarquardt

class OptimizedModel:
    def __init__(self, solver='lm', **kwargs):
        """
        Wrapper model for numerical IK solvers to expose a scikit-learn like interface.
        
        Args:
            solver: 'lm' for Levenberg-Marquardt, 'dls' for Damped Least Squares
            **kwargs: arguments passed to the underlying solver
        """
        self.solver_name = solver
        if solver == 'lm':
            self.solver = LevenbergMarquardt(**kwargs)
        elif solver == 'dls':
            self.solver = DampedLeastSquares(**kwargs)
        else:
            raise ValueError(f"Unknown solver {solver}. Choose 'lm' or 'dls'.")
            
    def fit(self, X, y=None):
        """No training needed for mathematical optimizers."""
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict joint angles.
        
        Args:
            X: DataFrame containing unscaled 'x', 'y', 'l1', 'l2' columns.
               (If using in a pipeline where features are scaled, ensure you pass the unscaled columns to this model).
        Returns:
            Numpy array of shape (N, 2) containing [q1, q2] predictions.
        """
        # Ensure necessary columns exist
        required_cols = ['x', 'y', 'l1', 'l2']
        for col in required_cols:
            if col not in X.columns:
                raise ValueError(f"OptimizedModel requires the '{col}' column in the input DataFrame.")
                
        predictions = []
        for _, row in X.iterrows():
            target_x = row['x']
            target_y = row['y']
            l1 = row['l1']
            l2 = row['l2']
            
            # Using [0.1, 0.1] as a simple initial guess for iterative solvers
            initial_q = [0.1, 0.1]
            
            q = self.solver.solve(target_x, target_y, initial_q, (l1, l2))
            predictions.append(q)
            
        return np.array(predictions)
