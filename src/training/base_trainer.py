from abc import ABC, abstractmethod
import pandas as pd
import joblib
from pathlib import Path
from src.utils.logging_utils import get_logger

class BaseTrainer(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.logger = get_logger(self.__class__.__name__)
        self.model = None
        
    @abstractmethod
    def build_model(self, config: dict):
        pass
        
    def train(self, X_train: pd.DataFrame, y_train: pd.DataFrame):
        self.logger.info(f"Training {self.model_name}...")
        if self.model is None:
            raise ValueError("Model is not built yet!")
        self.model.fit(X_train, y_train)
        self.logger.info(f"Training complete for {self.model_name}.")
        
    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        if self.model is None:
            raise ValueError("Model is not trained/loaded!")
        preds = self.model.predict(X)
        # Ensure it returns a dataframe with same index if X is DataFrame
        return pd.DataFrame(preds, index=X.index, columns=['q1', 'q2'])
        
    def save(self, path: Path):
        self.logger.info(f"Saving model to {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        
    def load(self, path: Path):
        self.logger.info(f"Loading model from {path}")
        self.model = joblib.load(path)
