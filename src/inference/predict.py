import argparse
import pandas as pd
import joblib
import numpy as np
from pathlib import Path
from src.utils.paths import MODELS_DIR
from src.features.feature_engineering import FeatureEngineer
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

class ManipulatorPredictor:
    def __init__(self, model_name: str = "xgboost"):
        self.model_name = model_name
        self.logger = get_logger(self.__class__.__name__)
        
        self.scaler_path = MODELS_DIR / "scaler.pkl"
        self.model_path = MODELS_DIR / f"{model_name}_model.pkl"
        
        if not self.scaler_path.exists() or not self.model_path.exists():
            raise FileNotFoundError(f"Scaler or Model '{model_name}' not found in {MODELS_DIR}. Train the model first.")
            
        self.scaler = joblib.load(self.scaler_path)
        self.model = joblib.load(self.model_path)
        self.engineer = FeatureEngineer()
        
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predicts joint angles for given Cartesian coordinates and link lengths.
        df must contain 'x', 'y', 'l1', 'l2' columns.
        """
        # 1. Feature Engineering
        df_engineered = self.engineer.transform(df.copy())
        
        # 2. Scale Features
        feature_cols = [c for c in df_engineered.columns if c not in ['q1', 'q2']]
        
        X_scaled = pd.DataFrame(
            self.scaler.feature_scaler.transform(df_engineered[feature_cols]),
            columns=feature_cols,
            index=df.index
        )
        
        # 3. Predict
        preds_scaled = self.model.predict(X_scaled)
        
        # Handle models returning 1D vs 2D arrays natively
        if len(preds_scaled.shape) == 1:
            preds_scaled = preds_scaled.reshape(1, -1)
            
        preds_df = pd.DataFrame(preds_scaled, columns=['q1', 'q2'], index=df.index)
        
        # 4. Inverse Scale Targets
        preds = self.scaler.inverse_transform_targets(preds_df)
        
        return preds

def main():
    parser = argparse.ArgumentParser(description="2DOF Universal Manipulator Inverse Kinematics Inference")
    parser.add_argument('--x', type=float, help="Target X coordinate")
    parser.add_argument('--y', type=float, help="Target Y coordinate")
    parser.add_argument('--l1', type=float, default=1.0, help="Target L1 length")
    parser.add_argument('--l2', type=float, default=1.0, help="Target L2 length")
    parser.add_argument('--csv', type=str, help="Path to input CSV with 'x', 'y', 'l1', 'l2' columns")
    parser.add_argument('--model', type=str, default="xgboost", help="Model name to use")
    
    args = parser.parse_args()
    
    if args.csv:
        df = pd.read_csv(args.csv)
        for col in ['x', 'y', 'l1', 'l2']:
            if col not in df.columns:
                logger.error(f"CSV must contain '{col}' column")
                return
    elif args.x is not None and args.y is not None:
        df = pd.DataFrame({'x': [args.x], 'y': [args.y], 'l1': [args.l1], 'l2': [args.l2]})
    else:
        parser.print_help()
        return
        
    try:
        predictor = ManipulatorPredictor(model_name=args.model)
    except FileNotFoundError as e:
        logger.error(e)
        return
        
    predictions = predictor.predict(df)
    
    # Combine inputs and outputs
    results = pd.concat([df[['x', 'y', 'l1', 'l2']], predictions], axis=1)
    
    if args.csv:
        output_path = Path(args.csv).parent / "predictions.csv"
        results.to_csv(output_path, index=False)
        logger.info(f"Predictions saved to {output_path}")
    
    # Print results to console
    print("\n--- Predictions ---")
    print(results.to_string(index=False))

if __name__ == "__main__":
    main()
