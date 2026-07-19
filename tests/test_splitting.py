import pandas as pd
from src.splitting.splitter import get_train_val_test_splits

def test_train_val_test_splits():
    df = pd.DataFrame({'a': range(100)})
    train, val, test = get_train_val_test_splits(df)
    
    # 70-15-15 split of 100 is 70, 15, 15
    assert len(train) == 70
    assert len(val) == 15
    assert len(test) == 15
