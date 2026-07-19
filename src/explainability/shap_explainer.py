import shap
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.utils.paths import MODELS_DIR, RAW_DATA_PATH, OUTPUTS_DIR
from src.features.feature_engineering import FeatureEngineer
from src.preprocessing.scaler import DataScaler
from src.splitting.splitter import get_train_val_test_splits
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def explain_model(model_name: str = "xgboost"):
    logger.info(f"Generating SHAP explanations for {model_name}...")
    
    # 1. Load Data
    df = pd.read_csv(RAW_DATA_PATH)
    engineer = FeatureEngineer()
    df_engineered = engineer.transform(df)
    _, _, test_df = get_train_val_test_splits(df_engineered)
    
    # 2. Load Scaler and Model
    scaler = joblib.load(MODELS_DIR / "scaler.pkl")
    model = joblib.load(MODELS_DIR / f"{model_name}_model.pkl")
    
    feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
    X_test, _ = scaler.transform(test_df)
    
    # Use a small background dataset for SHAP to save time
    background = shap.sample(X_test, 100)
    
    explainer = shap.Explainer(model, background)
    shap_values = explainer(background)
    
    outputs_dir = OUTPUTS_DIR / "explainability"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Plot for q1
        plt.figure()
        shap.summary_plot(shap_values[:, :, 0] if len(shap_values.shape) == 3 else shap_values[0], background, show=False)
        plt.tight_layout()
        plt.savefig(outputs_dir / f"{model_name}_shap_q1.png")
        plt.close()
        
        # Plot for q2
        plt.figure()
        shap.summary_plot(shap_values[:, :, 1] if len(shap_values.shape) == 3 else shap_values[1], background, show=False)
        plt.tight_layout()
        plt.savefig(outputs_dir / f"{model_name}_shap_q2.png")
        plt.close()
        
        logger.info(f"SHAP plots saved to {outputs_dir}")
    except Exception as e:
        logger.error(f"Failed to generate SHAP plots: {e}")

if __name__ == "__main__":
    explain_model("xgboost")
