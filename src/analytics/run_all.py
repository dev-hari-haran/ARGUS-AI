import subprocess
import sys
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

def run_script(script_name):
    logger.info(f"--- Running {script_name} ---")
    subprocess.run([sys.executable, "-m", f"src.analytics.{script_name}"], check=True)

def main():
    try:
        run_script("data_explorer")
        run_script("model_diagnostics")
        run_script("robotics_viz")
        run_script("pdf_compiler")
        logger.info("All analytics successfully completed and PDFs compiled!")
    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while running analytics: {e}")

if __name__ == "__main__":
    main()
