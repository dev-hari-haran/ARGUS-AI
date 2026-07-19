import pandas as pd
import numpy as np
import pytest
from src.preprocessing.scaler import DataScaler

def test_data_scaler():
    train_df = pd.DataFrame({'f1': [1, 2, 3], 'f2': [4, 5, 6], 't1': [10, 20, 30], 't2': [0.1, 0.2, 0.3]})
    test_df = pd.DataFrame({'f1': [4, 5], 'f2': [7, 8], 't1': [40, 50], 't2': [0.4, 0.5]})
    
    scaler = DataScaler(feature_cols=['f1', 'f2'], target_cols=['t1', 't2'])
    
    with pytest.raises(ValueError):
        scaler.transform(train_df) # Not fitted yet
        
    scaler.fit(train_df)
    X_train, y_train = scaler.transform(train_df)
    X_test, y_test = scaler.transform(test_df)
    
    # Mean of standard scaled train should be 0
    assert np.isclose(X_train['f1'].mean(), 0.0)
    assert np.isclose(y_train['t1'].mean(), 0.0)
    
    # Mean of test should not necessarily be 0
    assert not np.isclose(X_test['f1'].mean(), 0.0)
    
    # Inverse transform
    y_test_inv = scaler.inverse_transform_targets(y_test)
    assert np.allclose(y_test_inv['t1'], test_df['t1'])
