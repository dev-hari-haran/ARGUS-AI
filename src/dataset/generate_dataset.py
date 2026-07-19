import numpy as np
import pandas as pd
from src.utils.config_loader import load_config
from src.utils.logging_utils import get_logger
from src.utils.paths import RAW_DATA_PATH, ensure_directories
from src.kinematics.forward_kinematics import ForwardKinematics

logger = get_logger(__name__)

def generate_dataset():
    ensure_directories()
    
    dataset_cfg = load_config('dataset')
    robot_cfg = load_config('robot')
    
    num_samples = dataset_cfg.get('num_samples', 1000000)
    seed = dataset_cfg.get('seed', 42)
    branch_policy = dataset_cfg.get('branch_policy', 'both')
    
    q1_limits = robot_cfg['joint_limits']['q1']
    q2_limits = robot_cfg['joint_limits']['q2']
    l1_limits = robot_cfg['link_lengths']['l1']
    l2_limits = robot_cfg['link_lengths']['l2']
    
    np.random.seed(seed)
    logger.info(f"Generating {num_samples} samples with branch policy: {branch_policy}")
    
    # Pre-allocate arrays
    q1 = np.random.uniform(q1_limits[0], q1_limits[1], num_samples)
    q2 = np.random.uniform(q2_limits[0], q2_limits[1], num_samples)
    l1 = np.random.uniform(l1_limits[0], l1_limits[1], num_samples)
    l2 = np.random.uniform(l2_limits[0], l2_limits[1], num_samples)
    
    if branch_policy == "positive_q2":
        q2 = np.abs(q2)
    elif branch_policy == "negative_q2":
        q2 = -np.abs(q2)
        
    fk = ForwardKinematics()
    x, y = fk.compute(q1, q2, l1, l2)
    
    df = pd.DataFrame({
        'x': x,
        'y': y,
        'l1': l1,
        'l2': l2,
        'q1': q1,
        'q2': q2
    })
    
    df.to_csv(RAW_DATA_PATH, index=False)
    logger.info(f"Dataset saved to {RAW_DATA_PATH}")

if __name__ == "__main__":
    generate_dataset()
