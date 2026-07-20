import os
import glob
import shutil
import json
from pathlib import Path

# Paths
base_dir = Path(r"r:\Developments\ML_Manipulator")
outputs_dir = base_dir / "outputs"
webapp_public = base_dir / "webapp" / "public" / "graphs"
data_dir = base_dir / "webapp" / "src" / "data"

# Create directories
webapp_public.mkdir(parents=True, exist_ok=True)
data_dir.mkdir(parents=True, exist_ok=True)

# Find all png files
png_files = glob.glob(str(outputs_dir / "**" / "*.png"), recursive=True)

graph_data = []

def format_title(filename):
    name = Path(filename).stem
    # Replace underscores with spaces and title case
    title = name.replace("_", " ").title()
    return title

def determine_category(filepath):
    path_str = str(filepath).lower()
    if "data_understanding" in path_str:
        return "Data Understanding"
    elif "model_diagnostics" in path_str:
        return "Model Diagnostics"
    elif "robotics" in path_str:
        return "Robotics & Kinematics"
    elif "explainability" in path_str:
        return "Explainability (SHAP)"
    elif "reports" in path_str:
        return "Performance Reports"
    return "General Output"

def determine_description(title, category):
    base_desc = f"This is a detailed {category.lower()} visualization focusing on {title.lower()}."
    if category == "Data Understanding":
        return base_desc + " It provides insight into the underlying distribution and patterns present in the kinematic dataset."
    elif category == "Model Diagnostics":
        return base_desc + " It highlights the regression performance and error residuals to identify potential biases or variance."
    elif category == "Robotics & Kinematics":
        return base_desc + " This helps confirm that the physical joint space and Cartesian workspace constraints are being respected."
    elif category == "Explainability (SHAP)":
        return base_desc + " By decomposing predictions, we can clearly see which physical features drive the model's decision-making."
    elif category == "Performance Reports":
        return base_desc + " These reports aggregate the overall findings to give a high-level summary of model superiority."
    return base_desc + " It is essential for understanding the broader performance metrics."

for filepath in png_files:
    path = Path(filepath)
    filename = path.name
    
    # Copy to public/graphs
    dest = webapp_public / filename
    shutil.copy(filepath, dest)
    
    # Metadata
    title = format_title(filename)
    category = determine_category(path)
    description = determine_description(title, category)
    
    graph_data.append({
        "id": path.stem,
        "filename": f"/graphs/{filename}",
        "title": title,
        "category": category,
        "description": description
    })

# Write JSON
json_path = data_dir / "graphsData.json"
with open(json_path, "w") as f:
    json.dump(graph_data, f, indent=2)

print(f"Copied {len(graph_data)} graphs and generated {json_path}")
