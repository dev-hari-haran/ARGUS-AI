import pandas as pd
from pathlib import Path
from src.training.base_trainer import BaseTrainer
from src.Optimizer_Model.ml_wrapped_optimizer import MLWrappedOptimizer
from src.utils.paths import MODELS_DIR, RAW_DATA_PATH
from src.features.feature_engineering import FeatureEngineer
from src.preprocessing.scaler import DataScaler
from src.splitting.splitter import get_train_val_test_splits

class IKTrainer(BaseTrainer):
    def __init__(self, solver: str):
        super().__init__(f"ik_{solver}")
        self.solver = solver
        
    def build_model(self, config: dict):
        self.model = MLWrappedOptimizer(solver=self.solver)
        
    def train(self, X_train: pd.DataFrame, y_train: pd.DataFrame):
        self.logger.info(f"Preparing {self.model_name}...")
        self.model.fit(X_train, y_train)

def run_training_pipeline():
    df = pd.read_csv(RAW_DATA_PATH)
    engineer = FeatureEngineer()
    df_engineered = engineer.transform(df)
    train_df, _, _ = get_train_val_test_splits(df_engineered)
    
    feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
    target_cols = ['q1', 'q2']
    
    # We must ensure the scaler exists. It should if other models have been trained.
    scaler_path = MODELS_DIR / "scaler.pkl"
    if not scaler_path.exists():
        scaler = DataScaler(feature_cols, target_cols)
        scaler.fit(train_df)
        import joblib
        joblib.dump(scaler, scaler_path)
    
    # We don't actually need the data to fit IK, just empty dataframes, 
    # but passing actual for API completeness.
    dummy_X = pd.DataFrame()
    dummy_y = pd.DataFrame()
    
    for solver in ['dls', 'lm']:
        trainer = IKTrainer(solver)
        trainer.build_model({})
        trainer.train(dummy_X, dummy_y)
        trainer.save(MODELS_DIR / f"{trainer.model_name}_model.pkl")

if __name__ == "__main__":
    run_training_pipeline()
