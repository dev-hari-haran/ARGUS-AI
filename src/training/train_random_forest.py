import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from src.utils.config_loader import load_config
from src.utils.paths import MODELS_DIR, RAW_DATA_PATH
from src.training.base_trainer import BaseTrainer
from src.features.feature_engineering import FeatureEngineer
from src.preprocessing.scaler import DataScaler
from src.splitting.splitter import get_train_val_test_splits
import joblib

class RandomForestTrainer(BaseTrainer):
    def __init__(self):
        super().__init__("random_forest")
        
    def build_model(self, config: dict):
        self.model = RandomForestRegressor(
            n_estimators=config.get('n_estimators', 100),
            max_depth=config.get('max_depth', None),
            min_samples_split=config.get('min_samples_split', 2),
            random_state=config.get('random_state', 42),
            n_jobs=config.get('n_jobs', -1),
            verbose=2
        )

def run_training_pipeline():
    # 1. Load data
    df = pd.read_csv(RAW_DATA_PATH)
    
    # 2. Feature Engineering
    engineer = FeatureEngineer()
    df_engineered = engineer.transform(df)
    
    # 3. Split
    train_df, val_df, test_df = get_train_val_test_splits(df_engineered)
    
    # 4. Scale
    feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
    target_cols = ['q1', 'q2']
    
    scaler = DataScaler(feature_cols, target_cols)
    scaler.fit(train_df)
    
    X_train, y_train = scaler.transform(train_df)
    X_val, y_val = scaler.transform(val_df)
    X_test, y_test = scaler.transform(test_df)
    
    # 5. Train
    rf_config = load_config('models/random_forest')
    trainer = RandomForestTrainer()
    trainer.build_model(rf_config)
    trainer.train(X_train, y_train)
    
    # Save artifacts
    trainer.save(MODELS_DIR / "random_forest_model.pkl")
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    
    # Validation
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
