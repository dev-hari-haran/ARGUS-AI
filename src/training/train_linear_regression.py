import os
import pandas as pd
from tqdm import tqdm
from sklearn.linear_model import LinearRegression
from src.utils.config_loader import load_config
from src.utils.paths import MODELS_DIR, RAW_DATA_PATH
from src.training.base_trainer import BaseTrainer
from src.features.feature_engineering import FeatureEngineer
from src.preprocessing.scaler import DataScaler
from src.splitting.splitter import get_train_val_test_splits
import joblib

class LinearRegressionTrainer(BaseTrainer):
    def __init__(self):
        super().__init__("linear_regression")
        
    def build_model(self, config: dict):
        self.model = LinearRegression(
            n_jobs=config.get('n_jobs', -1)
        )
        
    def train(self, X_train, y_train):
        self.logger.info(f"Training {self.model_name}...")
        # Since sklearn LinearRegression doesn't have native progress bar,
        # we just log that it started. For 100M rows, OLS might take a few minutes.
        self.model.fit(X_train, y_train)
        self.logger.info(f"Training complete for {self.model_name}.")

def run_training_pipeline():
    # 1. Load Data with Progress
    print("Loading huge dataset (100M rows) into Memory...")
    # Read in chunks to show progress
    chunk_size = 5_000_000
    df_list = []
    
    with tqdm(desc="Reading CSV into RAM") as pbar:
        for chunk in pd.read_csv(RAW_DATA_PATH, chunksize=chunk_size):
            df_list.append(chunk)
            pbar.update(len(chunk))
            
    df = pd.concat(df_list, ignore_index=True)
    del df_list
    
    print("Applying Geometric Feature Engineering...")
    engineer = FeatureEngineer()
    df_engineered = engineer.transform(df)
    
    print("Splitting Data...")
    train_df, val_df, test_df = get_train_val_test_splits(df_engineered)
    
    feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
    target_cols = ['q1', 'q2']
    
    print("Fitting Scalers & Transforming Data (Progress tracked by steps)...")
    scaler = DataScaler(feature_cols, target_cols)
    scaler.fit(train_df)
    
    X_train, y_train = scaler.transform(train_df)
    X_val, y_val = scaler.transform(val_df)
    X_test, y_test = scaler.transform(test_df)
    
    model_config = load_config('models/linear_regression')
    trainer = LinearRegressionTrainer()
    trainer.build_model(model_config)
    
    # Train
    print("Initiating OLS Math Solver (Wait a few minutes)...")
    trainer.train(X_train, y_train)
    
    trainer.save(MODELS_DIR / "linear_regression_model.pkl")
    
    from src.evaluation.metrics import evaluate_predictions
    from src.visualization.plots import plot_joint_predictions, plot_error_distribution
    from src.utils.paths import OUTPUTS_DIR
    
    print("Evaluating Model on Test Set...")
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
