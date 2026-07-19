import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from pathlib import Path
from src.utils.paths import RAW_DATA_PATH, OUTPUTS_DIR
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def run_data_exploration():
    logger.info("Starting Data Exploration...")
    df = pd.read_csv(RAW_DATA_PATH)
    
    plots_dir = OUTPUTS_DIR / "plots" / "data_understanding"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Histograms & KDE
    logger.info("Generating Histograms & KDE...")
    for col in df.columns:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[col], kde=True, bins=50)
        plt.title(f'Histogram & KDE of {col}')
        plt.tight_layout()
        plt.savefig(plots_dir / f'hist_kde_{col}.png')
        plt.close()
        
    # 2. Box & Violin Plots
    logger.info("Generating Box & Violin Plots...")
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df)
    plt.title('Box Plot of All Features')
    plt.tight_layout()
    plt.savefig(plots_dir / 'box_plot_all.png')
    plt.close()
    
    plt.figure(figsize=(12, 6))
    # Subsample for violin to avoid massive rendering time
    sns.violinplot(data=df.sample(min(10000, len(df))))
    plt.title('Violin Plot of All Features (Subsampled)')
    plt.tight_layout()
    plt.savefig(plots_dir / 'violin_plot_all.png')
    plt.close()
    
    # 3. Correlation Heatmap
    logger.info("Generating Correlation Heatmaps...")
    plt.figure(figsize=(10, 8))
    corr = df.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(plots_dir / 'correlation_heatmap.png')
    plt.close()
    
    # Clustered Heatmap
    sns.clustermap(corr, cmap='coolwarm', annot=True)
    plt.title('Clustered Correlation Heatmap')
    plt.tight_layout()
    plt.savefig(plots_dir / 'clustered_heatmap.png')
    plt.close()
    
    # 4. Pair Plot (Subsampled)
    logger.info("Generating Pair Plot (N=1000)...")
    sns.pairplot(df.sample(min(1000, len(df))), corner=True)
    plt.savefig(plots_dir / 'pair_plot.png')
    plt.close()
    
    # 5. Dimensionality Reduction (PCA & t-SNE)
    logger.info("Generating PCA & t-SNE (N=5000)...")
    sample_df = df.sample(min(5000, len(df)), random_state=42)
    features = sample_df[['x', 'y', 'l1', 'l2']]
    
    pca = PCA(n_components=2)
    pca_res = pca.fit_transform(features)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=pca_res[:,0], y=pca_res[:,1], hue=sample_df['q1'], palette='viridis')
    plt.title('PCA Scatter Plot (colored by q1)')
    plt.tight_layout()
    plt.savefig(plots_dir / 'pca_scatter.png')
    plt.close()
    
    tsne = TSNE(n_components=2, random_state=42)
    tsne_res = tsne.fit_transform(features)
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=tsne_res[:,0], y=tsne_res[:,1], hue=sample_df['q2'], palette='plasma')
    plt.title('t-SNE Plot (colored by q2)')
    plt.tight_layout()
    plt.savefig(plots_dir / 'tsne_plot.png')
    plt.close()
    
    # 6. Missing Values
    logger.info("Generating Missing Values Bar Plot...")
    plt.figure(figsize=(8, 5))
    df.isnull().sum().plot(kind='bar')
    plt.title('Missing Value Bar Plot')
    plt.tight_layout()
    plt.savefig(plots_dir / 'missing_values_bar.png')
    plt.close()

if __name__ == "__main__":
    run_data_exploration()
