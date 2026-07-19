import os
from pathlib import Path
from PIL import Image
from src.utils.paths import OUTPUTS_DIR
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def compile_pdfs():
    logger.info("Compiling PDFs from generated plots...")
    plots_dir = OUTPUTS_DIR / "plots"
    docs_dir = OUTPUTS_DIR / "Plot_Documents"
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    if not plots_dir.exists():
        logger.error("No plots directory found. Run the analytics scripts first.")
        return
        
    categories = ['data_understanding', 'model_diagnostics', 'robotics']
    
    for category in categories:
        cat_dir = plots_dir / category
        if not cat_dir.exists():
            continue
            
        images = []
        for img_path in sorted(cat_dir.glob("*.png")):
            try:
                img = Image.open(img_path).convert('RGB')
                images.append(img)
            except Exception as e:
                logger.error(f"Failed to load image {img_path}: {e}")
                
        if images:
            pdf_path = docs_dir / f"{category}_report.pdf"
            images[0].save(pdf_path, save_all=True, append_images=images[1:])
            logger.info(f"Compiled {len(images)} images into {pdf_path}")

if __name__ == "__main__":
    compile_pdfs()
