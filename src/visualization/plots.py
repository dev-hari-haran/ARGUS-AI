import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

def plot_error_distribution(errors: np.ndarray, model_name: str, output_dir: Path):
    """
    Plots the distribution of Cartesian errors and saves in multiple formats.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(10, 6))
    sns.histplot(errors, bins=50, kde=True)
    plt.title(f'Cartesian Error Distribution - {model_name}')
    plt.xlabel('Error (Euclidean Distance)')
    plt.ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig(output_dir / f"{model_name}_error_dist.png")
    plt.savefig(output_dir / f"{model_name}_error_dist.pdf")
    plt.savefig(output_dir / f"{model_name}_error_dist.svg")
    plt.close()

def plot_joint_predictions(y_true: pd.DataFrame, y_pred: pd.DataFrame, model_name: str, output_dir: Path, sample_size: int = 100):
    """
    Scatter plot of True vs Predicted joint angles for a random sample.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Subsample for clearer visualization
    if len(y_true) > sample_size:
        indices = np.random.choice(len(y_true), sample_size, replace=False)
        y_true = y_true.iloc[indices]
        y_pred = y_pred.iloc[indices]
        
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    for i, col in enumerate(['q1', 'q2']):
        axes[i].scatter(y_true[col], y_pred[col], alpha=0.6)
        axes[i].plot([y_true[col].min(), y_true[col].max()], 
                     [y_true[col].min(), y_true[col].max()], 'r--')
        axes[i].set_title(f'{model_name}: True vs Predicted {col.upper()}')
        axes[i].set_xlabel('True')
        axes[i].set_ylabel('Predicted')
        
    plt.tight_layout()
    plt.savefig(output_dir / f"{model_name}_joint_preds.png")
    plt.close()

def plot_bias_variance_tradeoff(results_df: pd.DataFrame, output_dir: Path):
    """
    Plots the Bias vs Variance tradeoff for multiple models based on Cartesian Error.
    results_df must be indexed by model name and contain 'cartesian_mean_error' and 'cartesian_std_error'.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(10, 6))
    
    sns.scatterplot(
        data=results_df, 
        x='cartesian_mean_error', 
        y='cartesian_std_error', 
        hue=results_df.index,
        s=200,
        palette='tab10'
    )
    
    for idx, row in results_df.iterrows():
        plt.annotate(
            idx, 
            (row['cartesian_mean_error'], row['cartesian_std_error']),
            xytext=(10, 10),
            textcoords='offset points'
        )
        
    plt.title('Bias vs Variance Tradeoff (Cartesian Error)')
    plt.xlabel('Bias Proxy (Mean Cartesian Error)')
    plt.ylabel('Variance Proxy (Std Dev of Cartesian Error)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'bias_variance_tradeoff.png')
    plt.savefig(output_dir / 'bias_variance_tradeoff.pdf')
    plt.savefig(output_dir / 'bias_variance_tradeoff.svg')
    plt.close()

def plot_model_comparison_errors(model_errors: dict, output_dir: Path):
    """
    Plots a combined boxplot of Cartesian errors for multiple models.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plt.figure(figsize=(12, 6))
    
    # Convert dict of arrays to DataFrame directly
    df_errors = pd.DataFrame(model_errors)
    df_melted = df_errors.melt(var_name='Model', value_name='Cartesian Error')
    
    # Subsample to avoid memory/rendering freeze on huge datasets
    if len(df_melted) > 100000:
        df_melted = df_melted.sample(100000, random_state=42)
        
    sns.boxplot(data=df_melted, x='Model', y='Cartesian Error', palette='tab10')
    plt.title('Cartesian Error Distribution Comparison')
    plt.ylabel('Cartesian Error (Euclidean Distance)')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'model_comparison_errors.png')
    plt.savefig(output_dir / 'model_comparison_errors.pdf')
    plt.savefig(output_dir / 'model_comparison_errors.svg')
    plt.close()
