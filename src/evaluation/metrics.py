import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from src.kinematics.forward_kinematics import ForwardKinematics

def evaluate_predictions(y_true: pd.DataFrame, y_pred: pd.DataFrame, l1: np.ndarray, l2: np.ndarray, return_errors: bool = False):
    """
    Evaluates both Joint-Space metrics and Cartesian-Space (End-effector) metrics.
    Assumes y_true and y_pred contain 'q1' and 'q2' columns.
    Requires l1 and l2 arrays for Cartesian evaluation.
    """
    metrics = {}
    
    # Joint Space Metrics
    for col in ['q1', 'q2']:
        metrics[f'{col}_rmse'] = np.sqrt(mean_squared_error(y_true[col], y_pred[col]))
        metrics[f'{col}_mae'] = mean_absolute_error(y_true[col], y_pred[col])
        metrics[f'{col}_r2'] = r2_score(y_true[col], y_pred[col])
        
    # Cartesian Space Metrics (Forward Kinematics error)
    fk = ForwardKinematics()
    
    # True positions
    x_true, y_true_cart = fk.compute(y_true['q1'].values, y_true['q2'].values, l1, l2)
    
    # Predicted positions
    x_pred, y_pred_cart = fk.compute(y_pred['q1'].values, y_pred['q2'].values, l1, l2)
    
    # Euclidean distance error
    errors = np.sqrt((x_true - x_pred)**2 + (y_true_cart - y_pred_cart)**2)
    metrics['cartesian_mean_error'] = np.mean(errors)
    metrics['cartesian_max_error'] = np.max(errors)
    metrics['cartesian_std_error'] = np.std(errors)
    
    if return_errors:
        return metrics, errors
    return metrics
