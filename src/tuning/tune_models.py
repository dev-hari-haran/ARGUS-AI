import optuna
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error
from src.utils.config_loader import load_config
from src.utils.paths import RAW_DATA_PATH, MODELS_DIR, CONFIG_DIR
from src.features.feature_engineering import FeatureEngineer
from src.preprocessing.scaler import DataScaler
from src.splitting.splitter import get_train_val_test_splits
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def tune_xgboost():
    config = load_config('tuning/xgboost_tuning')
    
    # 1. Load Data
    df = pd.read_csv(RAW_DATA_PATH)
    engineer = FeatureEngineer()
    df_engineered = engineer.transform(df)
    train_df, val_df, _ = get_train_val_test_splits(df_engineered)
    
    feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
    target_cols = ['q1', 'q2']
    
    scaler = DataScaler(feature_cols, target_cols)
    scaler.fit(train_df)
    
    X_train, y_train = scaler.transform(train_df)
    X_val, y_val = scaler.transform(val_df)
    
    def objective(trial):
        n_estimators = trial.suggest_int('n_estimators', config['params']['n_estimators'][0], config['params']['n_estimators'][1])
        max_depth = trial.suggest_int('max_depth', config['params']['max_depth'][0], config['params']['max_depth'][1])
        learning_rate = trial.suggest_float('learning_rate', config['params']['learning_rate'][0], config['params']['learning_rate'][1], log=True)
        
        model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=42,
            n_jobs=-1,
            verbosity=0
        )
        
        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        
        # We optimize for total MSE on validation set
        mse = mean_squared_error(y_val, preds)
        return mse

    study = optuna.create_study(direction='minimize')
    logger.info(f"Starting Optuna tuning for XGBoost with {config['n_trials']} trials...")
    study.optimize(objective, n_trials=config['n_trials'])
    
    logger.info(f"Best trial: {study.best_trial.value}")
    logger.info(f"Best params: {study.best_params}")
    
    # Save the best params to a yaml file
    import yaml
    best_params_path = CONFIG_DIR / "models" / "xgboost_best.yaml"
    best_params_path.parent.mkdir(parents=True, exist_ok=True)
    with open(best_params_path, 'w') as f:
        yaml.dump(study.best_params, f)
    logger.info(f"Saved best params to {best_params_path}")

if __name__ == "__main__":
    tune_xgboost()
