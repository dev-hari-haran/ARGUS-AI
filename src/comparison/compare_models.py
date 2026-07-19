import os
import pandas as pd
from pathlib import Path
import joblib
from src.utils.paths import MODELS_DIR, RAW_DATA_PATH, OUTPUTS_DIR
from src.features.feature_engineering import FeatureEngineer
from src.splitting.splitter import get_train_val_test_splits
from src.evaluation.metrics import evaluate_predictions
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def compare_all_models():
    models_to_compare = [
        "decision_tree",
        "extra_trees",
        "random_forest",
        "hist_gradient_boosting",
        "xgboost"
    ]
    
    logger.info("Starting model comparison...")
    
    # 1. Load Data
    df = pd.read_csv(RAW_DATA_PATH)
    engineer = FeatureEngineer()
    df_engineered = engineer.transform(df)
    _, _, test_df = get_train_val_test_splits(df_engineered)
    
    # 2. Load Scaler
    scaler_path = MODELS_DIR / "scaler.pkl"
    if not scaler_path.exists():
        logger.error("Scaler not found. Please train models first.")
        return
        
    scaler = joblib.load(scaler_path)
    
    # Transform test set
    feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
    target_cols = ['q1', 'q2']
    X_test, y_test = scaler.transform(test_df)
    y_test_unscaled = scaler.inverse_transform_targets(y_test)
    
    l1_vals = test_df['l1'].values
    l2_vals = test_df['l2'].values
    
    results = []
    model_errors = {}
    
    for model_name in models_to_compare:
        model_path = MODELS_DIR / f"{model_name}_model.pkl"
        if not model_path.exists():
            logger.warning(f"Model {model_name} not found. Skipping.")
            continue
            
        logger.info(f"Evaluating {model_name}...")
        try:
            model = joblib.load(model_path)
        except Exception as e:
            logger.error(f"Failed to load {model_name}: {e}. Skipping.")
            continue
        
        preds_scaled = model.predict(X_test)
        # Handle models returning 1D vs 2D arrays natively
        if len(preds_scaled.shape) == 1:
            preds_scaled = preds_scaled.reshape(1, -1)
        preds_df = pd.DataFrame(preds_scaled, columns=['q1', 'q2'], index=X_test.index)
        preds = scaler.inverse_transform_targets(preds_df)
        
        metrics, errors = evaluate_predictions(y_test_unscaled, preds, l1_vals, l2_vals, return_errors=True)
        metrics['model'] = model_name
        results.append(metrics)
        model_errors[model_name] = errors
        
    if not results:
        logger.error("No models were evaluated.")
        return
        
    # Compile report
    results_df = pd.DataFrame(results).set_index('model')
    
    # Sort by Cartesian Mean Error
    results_df = results_df.sort_values('cartesian_mean_error')
    
    reports_dir = OUTPUTS_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = reports_dir / "model_comparison.csv"
    results_df.to_csv(report_path)
    
    logger.info(f"Comparison report saved to {report_path}")
    
    # Print Markdown table
    logger.info("\n" + results_df[['cartesian_mean_error', 'cartesian_max_error', 'q1_r2', 'q2_r2']].to_markdown())
    
    # Plot Bias-Variance Tradeoff
    from src.visualization.plots import plot_bias_variance_tradeoff, plot_model_comparison_errors
    plot_bias_variance_tradeoff(results_df, reports_dir)
    logger.info(f"Bias-Variance tradeoff graph saved to {reports_dir}")
    
    # Plot Combined Error Boxplots
    plot_model_comparison_errors(model_errors, reports_dir)
    logger.info(f"Combined Error graph saved to {reports_dir}")

if __name__ == "__main__":
    compare_all_models()
