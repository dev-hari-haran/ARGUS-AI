import pandas as pd
from typing import Tuple
from sklearn.model_selection import train_test_split, KFold
from src.utils.config_loader import load_config

def get_train_val_test_splits(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits the dataset into train, validation, and test sets.
    """
    config = load_config('split')
    val_ratio = config.get('val_ratio', 0.15)
    test_ratio = config.get('test_ratio', 0.15)
    random_state = config.get('random_state', 42)
    
    # Calculate proportion of val+test out of the total
    val_test_ratio = val_ratio + test_ratio
    # Calculate proportion of test out of val+test
    test_prop_of_val_test = test_ratio / val_test_ratio
    
    # First split: Train vs (Val + Test)
    train_df, temp_df = train_test_split(
        df, test_size=val_test_ratio, random_state=random_state
    )
    
    # Second split: Val vs Test
    val_df, test_df = train_test_split(
        temp_df, test_size=test_prop_of_val_test, random_state=random_state
    )
    
    return train_df, val_df, test_df

def get_cv_splitter(n_splits: int = 5):
    """
    Returns a configured cross-validation splitter.
    """
    config = load_config('split')
    random_state = config.get('random_state', 42)
    return KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
