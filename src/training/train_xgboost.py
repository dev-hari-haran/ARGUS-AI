import os
import pandas as pd
import xgboost as xgb
from src.utils.config_loader import load_config
from src.utils.paths import MODELS_DIR, RAW_DATA_PATH
from src.training.base_trainer import BaseTrainer
from src.features.feature_engineering import FeatureEngineer
from src.preprocessing.scaler import DataScaler
from src.splitting.splitter import get_train_val_test_splits
import joblib

class XGBoostTrainer(BaseTrainer):
    def __init__(self):
        super().__init__("xgboost")
        
    def build_model(self, config: dict):
        self.model = xgb.XGBRegressor(
            n_estimators=config.get('n_estimators', 100),
            max_depth=config.get('max_depth', 6),
            learning_rate=config.get('learning_rate', 0.1),
            random_state=config.get('random_state', 42),
            n_jobs=config.get('n_jobs', -1),
            verbosity=2
        )

def run_training_pipeline():
    df = pd.read_csv(RAW_DATA_PATH)
    engineer = FeatureEngineer()
    df_engineered = engineer.transform(df)
    train_df, val_df, test_df = get_train_val_test_splits(df_engineered)
    
    feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
    target_cols = ['q1', 'q2']
    
    scaler = DataScaler(feature_cols, target_cols)
    scaler.fit(train_df)
    
    X_train, y_train = scaler.transform(train_df)
    X_val, y_val = scaler.transform(val_df)
    X_test, y_test = scaler.transform(test_df)
    
    model_config = load_config('models/xgboost')
    trainer = XGBoostTrainer()
    trainer.build_model(model_config)
    trainer.train(X_train, y_train)
    
    trainer.save(MODELS_DIR / "xgboost_model.pkl")
    
    from src.evaluation.metrics import evaluate_predictions
    from src.visualization.plots import plot_joint_predictions, plot_error_distribution
    from src.utils.paths import OUTPUTS_DIR
    
    preds_scaled = trainer.predict(X_test)
    preds = scaler.inverse_transform_targets(preds_scaled)
    y_test_unscaled = scaler.inverse_transform_targets(y_test)
    
    metrics, errors = evaluate_predictions(y_test_unscaled, preds, test_df['l1'].values, test_df['l2'].values, return_errors=True)
    trainer.logger.info(f"Test Set Evaluation: {metrics}")
    
    reports_dir = OUTPUTS_DIR / "reports"
    plot_joint_predictions(y_test_unscaled, preds, trainer.model_name, reports_dir)
    plot_error_distribution(errors, trainer.model_name, reports_dir)

if __name__ == "__main__":
    run_training_pipeline()
