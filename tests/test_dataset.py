import os
import pandas as pd
import numpy as np
from src.utils.paths import RAW_DATA_PATH
from src.dataset.generate_dataset import generate_dataset

def test_generate_dataset():
    # Ensure any old file is removed
    if RAW_DATA_PATH.exists():
        RAW_DATA_PATH.unlink()
        
    # Generate small dataset
    generate_dataset()
    
    assert RAW_DATA_PATH.exists()
    
    df = pd.read_csv(RAW_DATA_PATH)
    assert not df.empty
    assert list(df.columns) == ['x', 'y', 'l1', 'l2', 'q1', 'q2']
    
    # Check branch policy for default config (positive_q2)
    assert np.all(df['q2'] >= 0.0)
