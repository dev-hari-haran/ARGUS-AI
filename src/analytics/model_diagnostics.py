import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
from src.utils.paths import RAW_DATA_PATH, MODELS_DIR, OUTPUTS_DIR
from src.features.feature_engineering import FeatureEngineer
from src.preprocessing.scaler import DataScaler
from src.splitting.splitter import get_train_val_test_splits
from src.utils.logging_utils import get_logger
import time

logger = get_logger(__name__)

def run_model_diagnostics():
    logger.info("Starting Model Diagnostics...")
    plots_dir = OUTPUTS_DIR / "plots" / "model_diagnostics"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.read_csv(RAW_DATA_PATH)
    engineer = FeatureEngineer()
    df_engineered = engineer.transform(df)
    _, _, test_df = get_train_val_test_splits(df_engineered)
    
    scaler = joblib.load(MODELS_DIR / "scaler.pkl")
    feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
    X_test, y_test = scaler.transform(test_df)
    y_test_unscaled = scaler.inverse_transform_targets(y_test)
    
    # Only evaluate models that were trained with the CURRENT feature engineering logic
    models = ["xgboost", "linear_regression"]
    
    inference_times = {}
    model_sizes = {}
    
    for model_name in models:
        model_path = MODELS_DIR / f"{model_name}_model.pkl"
        if not model_path.exists():
            continue
            
        model_sizes[model_name] = model_path.stat().st_size / (1024 * 1024) # MB
        
        try:
            model = joblib.load(model_path)
        except Exception:
            continue
        
        # Inference Time
        start = time.time()
        preds_scaled = model.predict(X_test)
        inference_times[model_name] = time.time() - start
        
        if len(preds_scaled.shape) == 1:
            preds_scaled = preds_scaled.reshape(1, -1)
        preds_df = pd.DataFrame(preds_scaled, columns=['q1', 'q2'], index=X_test.index)
        preds = scaler.inverse_transform_targets(preds_df)
        
        # Residuals
        res_q1 = y_test_unscaled['q1'] - preds['q1']
        res_q2 = y_test_unscaled['q2'] - preds['q2']
        
        plt.figure(figsize=(10, 5))
        sns.histplot(res_q1, bins=50, kde=True, color='blue', label='q1 residual', alpha=0.5)
        sns.histplot(res_q2, bins=50, kde=True, color='red', label='q2 residual', alpha=0.5)
        plt.title(f'Residual Histogram - {model_name}')
        plt.legend()
        plt.tight_layout()
        plt.savefig(plots_dir / f'{model_name}_residual_hist.png')
        plt.close()
        
        # Actual vs Predicted
        plt.figure(figsize=(8, 8))
        # Subsample scatter plot for speed
        subset = 5000
        plt.scatter(y_test_unscaled['q1'].iloc[:subset], preds['q1'].iloc[:subset], alpha=0.1, s=5)
        plt.plot([y_test_unscaled['q1'].min(), y_test_unscaled['q1'].max()], 
                 [y_test_unscaled['q1'].min(), y_test_unscaled['q1'].max()], 'r--')
        plt.title(f'Actual vs Predicted (q1) - {model_name}')
        plt.tight_layout()
        plt.savefig(plots_dir / f'{model_name}_actual_vs_pred_q1.png')
        plt.close()
        
    # Model Comparison Charts
    if inference_times:
        plt.figure(figsize=(8, 5))
        sns.barplot(x=list(inference_times.keys()), y=list(inference_times.values()))
        plt.title('Inference Time (Total Test Set) by Model')
        plt.ylabel('Seconds')
        plt.tight_layout()
        plt.savefig(plots_dir / 'inference_time_bar.png')
        plt.close()
        
    if model_sizes:
        plt.figure(figsize=(8, 5))
        sns.barplot(x=list(model_sizes.keys()), y=list(model_sizes.values()))
        plt.title('Model Size by Model')
        plt.ylabel('Size (MB)')
        plt.tight_layout()
        plt.savefig(plots_dir / 'model_size_bar.png')
        plt.close()

if __name__ == "__main__":
    run_model_diagnostics()
