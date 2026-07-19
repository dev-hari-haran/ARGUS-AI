import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.utils.paths import RAW_DATA_PATH, OUTPUTS_DIR
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def run_robotics_viz():
    logger.info("Starting Robotics Visualizations...")
    plots_dir = OUTPUTS_DIR / "plots" / "robotics"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.read_csv(RAW_DATA_PATH)
    sample_df = df.sample(min(10000, len(df)), random_state=42)
    
    # 1. Workspace Scatter Plot / Reachability Map
    logger.info("Generating Reachability Map...")
    plt.figure(figsize=(8, 8))
    sns.scatterplot(data=sample_df, x='x', y='y', hue='l1', palette='viridis', s=10, alpha=0.6)
    plt.title('Workspace Reachability Map (Colored by L1)')
    plt.axis('equal')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plots_dir / 'workspace_reachability.png')
    plt.close()
    
    # 2. Joint Space Scatter Plot
    logger.info("Generating Joint Space Scatter...")
    plt.figure(figsize=(8, 8))
    sns.scatterplot(data=sample_df, x='q1', y='q2', s=5, alpha=0.3, color='purple')
    plt.title('Joint Space Scatter Plot')
    plt.xlabel('q1 (radians)')
    plt.ylabel('q2 (radians)')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(plots_dir / 'joint_space_scatter.png')
    plt.close()
    
    # 3. Workspace Heatmap (Density)
    logger.info("Generating Workspace Heatmap...")
    plt.figure(figsize=(8, 8))
    sns.kdeplot(data=sample_df, x='x', y='y', fill=True, cmap='mako', thresh=0, levels=100)
    plt.title('Workspace Density Heatmap')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(plots_dir / 'workspace_heatmap.png')
    plt.close()

if __name__ == "__main__":
    run_robotics_viz()
