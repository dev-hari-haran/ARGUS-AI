import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib
from src.utils.paths import MODELS_DIR, RAW_DATA_PATH, OUTPUTS_DIR
from src.features.feature_engineering import FeatureEngineer
from src.preprocessing.scaler import DataScaler
from src.splitting.splitter import get_train_val_test_splits
from src.evaluation.metrics import evaluate_predictions
from src.visualization.plots import plot_error_distribution, plot_joint_predictions

def generate_graphs():
    reports_dir = OUTPUTS_DIR / "reports"
    
    # 1. Comparison Graph of Optimized & Non-Optimized Model
    csv_path = reports_dir / "model_comparison.csv"
    if csv_path.exists():
        df_results = pd.read_csv(csv_path)
        plt.figure(figsize=(12, 6))
        # Highlight optimized models
        colors = ['#2ca02c' if 'ik_' in m else '#1f77b4' for m in df_results['model']]
        sns.barplot(data=df_results, x='cartesian_mean_error', y='model', palette=colors)
        plt.title('Comparison of Optimized (Green) vs Non-Optimized (Blue) Models')
        plt.xlabel('Cartesian Mean Error (Log Scale - Lower is Better)')
        plt.ylabel('Model')
        plt.xscale('log')
        plt.tight_layout()
        plt.savefig(reports_dir / "Comparison_Graph.png")
        plt.close()
        print("Generated Comparison_Graph.png")
        
    # 2. Graph for Optimized Model ("Graph_Optimized")
    # Load data
    df = pd.read_csv(RAW_DATA_PATH)
    engineer = FeatureEngineer()
    df_engineered = engineer.transform(df)
    _, _, test_df = get_train_val_test_splits(df_engineered)
    
    feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
    target_cols = ['q1', 'q2']
    
    scaler = joblib.load(MODELS_DIR / "scaler.pkl")
    X_test, y_test = scaler.transform(test_df)
    y_test_unscaled = scaler.inverse_transform_targets(y_test)
    
    # Load IK LM model (our best Optimized Model)
    model_path = MODELS_DIR / "ik_lm_model.pkl"
    if model_path.exists():
        model = joblib.load(model_path)
        preds_scaled = model.predict(X_test)
        if len(preds_scaled.shape) == 1:
            preds_scaled = preds_scaled.reshape(1, -1)
        preds_df = pd.DataFrame(preds_scaled, columns=['q1', 'q2'], index=X_test.index)
        preds = scaler.inverse_transform_targets(preds_df)
        
        # We can plot the error distribution as Graph_Optimized
        metrics, errors = evaluate_predictions(
            y_test_unscaled, preds, test_df['l1'].values, test_df['l2'].values, return_errors=True
        )
        
        plt.figure(figsize=(10, 6))
        sns.histplot(errors, bins=50, kde=True, color='#2ca02c')
        plt.title('Cartesian Error Distribution - Optimized Model (IK LM)')
        plt.xlabel('Error (Euclidean Distance)')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(reports_dir / "Graph_Optimized.png")
        plt.close()
        print("Generated Graph_Optimized.png")
        
if __name__ == "__main__":
    generate_graphs()
